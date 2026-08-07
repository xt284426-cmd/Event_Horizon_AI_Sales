import argparse
import os
from datetime import datetime
from decimal import Decimal

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from backend.app.models import (
    Company,
    Conversation,
    ConversationMessage,
    Customer,
    Deal,
    User,
)
from test_data.education_demo.common import COMPANY_CODE, COMPANY_NAME, write_json
from test_data.education_demo.generate_conversations import generate_conversations
from test_data.education_demo.generate_customers import generate_customers
from test_data.education_demo.generate_deals import generate_deals
from test_data.education_demo.generate_sales import generate_sales


def parse_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value)


def generate_files() -> dict[str, int]:
    sales = generate_sales()
    customers = generate_customers()
    conversation_data = generate_conversations()
    deals = generate_deals()
    write_json("sales.json", sales)
    write_json("customers.json", customers)
    write_json("conversations.json", conversation_data["conversations"])
    write_json("messages.json", conversation_data["messages"])
    write_json("deals.json", deals)
    return {
        "sales": len(sales),
        "customers": len(customers),
        "conversations": len(conversation_data["conversations"]),
        "messages": len(conversation_data["messages"]),
        "deals": len(deals),
    }


def get_or_create_company(session: Session) -> Company:
    company = session.scalar(select(Company).where(Company.code == COMPANY_CODE))
    if company is None:
        company = Company(name=COMPANY_NAME, code=COMPANY_CODE, is_active=True)
        session.add(company)
        session.flush()
    else:
        company.name = COMPANY_NAME
        company.is_active = True
    return company


def seed_sales(session: Session, company: Company, records: list[dict]) -> dict[str, User]:
    users: dict[str, User] = {}
    for record in records:
        external_id = record["external_user_id"]
        user = session.scalar(
            select(User).where(
                User.company_id == company.id,
                User.external_user_id == external_id,
            )
        )
        values = {
            "name": record["name"],
            "email": record["email"],
            "role": record["role"],
            "is_active": True,
        }
        if user is None:
            user = User(company_id=company.id, external_user_id=external_id, **values)
            session.add(user)
            session.flush()
        else:
            for key, value in values.items():
                setattr(user, key, value)
        users[external_id] = user
    return users


def seed_customers(
    session: Session, company: Company, records: list[dict]
) -> dict[str, Customer]:
    customers: dict[str, Customer] = {}
    for record in records:
        external_id = record["external_customer_id"]
        customer = session.scalar(
            select(Customer).where(
                Customer.company_id == company.id,
                Customer.external_customer_id == external_id,
            )
        )
        values = {
            "name": record["name"],
            "phone": record["phone"],
            "email": record["email"],
            "source": record["source"],
            "status": record["status"],
            "extra_data": record["extra_data"],
        }
        if customer is None:
            customer = Customer(
                company_id=company.id,
                external_customer_id=external_id,
                **values,
            )
            session.add(customer)
            session.flush()
        else:
            for key, value in values.items():
                setattr(customer, key, value)
        customers[external_id] = customer
    return customers


def seed_conversations(
    session: Session,
    company: Company,
    customers: dict[str, Customer],
    users: dict[str, User],
    records: list[dict],
) -> dict[str, Conversation]:
    conversations: dict[str, Conversation] = {}
    for record in records:
        external_id = record["external_conversation_id"]
        conversation = session.scalar(
            select(Conversation).where(
                Conversation.company_id == company.id,
                Conversation.external_conversation_id == external_id,
            )
        )
        values = {
            "customer_id": customers[record["customer_external_id"]].id,
            "owner_user_id": users[record["sales_external_id"]].id,
            "channel": record["channel"],
            "started_at": parse_datetime(record["started_at"]),
            "ended_at": parse_datetime(record["ended_at"]),
        }
        if conversation is None:
            conversation = Conversation(
                company_id=company.id,
                external_conversation_id=external_id,
                **values,
            )
            session.add(conversation)
            session.flush()
        else:
            for key, value in values.items():
                setattr(conversation, key, value)
        conversations[external_id] = conversation
    return conversations


def seed_messages(
    session: Session,
    company: Company,
    conversations: dict[str, Conversation],
    records: list[dict],
) -> None:
    for record in records:
        external_id = record["external_message_id"]
        message = session.scalar(
            select(ConversationMessage).where(
                ConversationMessage.company_id == company.id,
                ConversationMessage.external_message_id == external_id,
            )
        )
        raw_data = {
            **record["raw_data"],
            "customer_external_id": record["customer_external_id"],
            "sales_external_id": record["sales_external_id"],
        }
        values = {
            "conversation_id": conversations[record["conversation_external_id"]].id,
            "sender_type": record["sender_type"],
            "sender_external_id": record["sender_external_id"],
            "message_type": record["message_type"],
            "content": record["content"],
            "raw_data": raw_data,
            "sent_at": parse_datetime(record["sent_at"]),
        }
        if message is None:
            message = ConversationMessage(
                company_id=company.id,
                external_message_id=external_id,
                **values,
            )
            session.add(message)
        else:
            for key, value in values.items():
                setattr(message, key, value)


def seed_deals(
    session: Session,
    company: Company,
    customers: dict[str, Customer],
    users: dict[str, User],
    records: list[dict],
) -> None:
    for record in records:
        customer = customers[record["customer_external_id"]]
        closed_at = parse_datetime(record["closed_at"])
        deal = session.scalar(
            select(Deal).where(
                Deal.company_id == company.id,
                Deal.customer_id == customer.id,
                Deal.title == record["title"],
                Deal.closed_at == closed_at,
            )
        )
        values = {
            "owner_user_id": users[record["sales_external_id"]].id,
            "amount": Decimal(str(record["amount"])),
            "currency": record["currency"],
            "stage": record["stage"],
            "closed_at": closed_at,
            "expected_close_date": closed_at.date(),
        }
        if deal is None:
            deal = Deal(
                company_id=company.id,
                customer_id=customer.id,
                title=record["title"],
                **values,
            )
            session.add(deal)
        else:
            for key, value in values.items():
                setattr(deal, key, value)


def seed_database(database_url: str) -> dict[str, int]:
    sales = generate_sales()
    customers_data = generate_customers()
    conversation_data = generate_conversations()
    deals = generate_deals()
    engine = create_engine(database_url)
    session_factory = sessionmaker(bind=engine, expire_on_commit=False)

    with session_factory.begin() as session:
        company = get_or_create_company(session)
        users = seed_sales(session, company, sales)
        customers = seed_customers(session, company, customers_data)
        conversations = seed_conversations(
            session,
            company,
            customers,
            users,
            conversation_data["conversations"],
        )
        seed_messages(session, company, conversations, conversation_data["messages"])
        seed_deals(session, company, customers, users, deals)

    return {
        "sales": len(sales),
        "customers": len(customers_data),
        "conversations": len(conversation_data["conversations"]),
        "messages": len(conversation_data["messages"]),
        "deals": len(deals),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate and seed education demo data")
    parser.add_argument(
        "--generate-only",
        action="store_true",
        help="Only generate JSON fixtures; do not connect to PostgreSQL",
    )
    args = parser.parse_args()

    if args.generate_only:
        counts = generate_files()
    else:
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            raise SystemExit("DATABASE_URL is required when seeding PostgreSQL")
        generate_files()
        counts = seed_database(database_url)

    print(" ".join(f"{name}={count}" for name, count in counts.items()))


if __name__ == "__main__":
    main()

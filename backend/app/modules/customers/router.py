from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.modules.customers.schemas import CustomerDetail, CustomerListItem
from backend.app.modules.customers.services import CustomerNotFoundError, CustomerService


router = APIRouter(prefix="/api/customers", tags=["customers"])
DatabaseSession = Annotated[Session, Depends(get_db)]


@router.get("", response_model=list[CustomerListItem])
def list_customers(
    session: DatabaseSession,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=500)] = 100,
) -> list[CustomerListItem]:
    return CustomerService(session).list_customers(offset=offset, limit=limit)


@router.get("/{customer_id}", response_model=CustomerDetail)
def get_customer(customer_id: int, session: DatabaseSession) -> CustomerDetail:
    try:
        return CustomerService(session).get_customer_detail(customer_id)
    except CustomerNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

import request from './request'

export function getCustomers(params = {}) {
  return request.get('/customers', { params })
}

export function getCustomerDetail(id) {
  return request.get(`/customers/${id}`)
}

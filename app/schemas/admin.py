from pydantic import BaseModel


class DashboardStats(BaseModel):
    revenue: float
    orders: int
    customers: int
    products: int
    low_stock_products: int
    pending_orders: int
    refunds: int
    average_order_value: float


class TimeSeriesPoint(BaseModel):
    label: str
    value: float


class CategorySalesPoint(BaseModel):
    category: str
    value: float


class TopProductPoint(BaseModel):
    product: str
    quantity: int


class AdminDashboardResponse(BaseModel):
    stats: DashboardStats

    revenue_over_time: list[TimeSeriesPoint]
    orders_over_time: list[TimeSeriesPoint]
    sales_by_category: list[CategorySalesPoint]
    top_products: list[TopProductPoint]
    new_customers: list[TimeSeriesPoint]
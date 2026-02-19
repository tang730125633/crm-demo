from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


class CustomerStatus(str, Enum):
    potential = "潜在客户"
    interested = "意向客户"
    closed = "成交客户"
    lost = "流失客户"


class FollowType(str, Enum):
    phone = "电话"
    wechat = "微信"
    visit = "拜访"
    email = "邮件"


# ---- FollowUp Schemas ----

class FollowUpCreate(BaseModel):
    content: str
    follow_type: FollowType = FollowType.phone

    @field_validator("content")
    @classmethod
    def content_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("跟进内容不能为空")
        return v.strip()


class FollowUpResponse(BaseModel):
    id: int
    customer_id: int
    content: str
    follow_type: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ---- Customer Schemas ----

class CustomerCreate(BaseModel):
    name: str
    phone: Optional[str] = ""
    email: Optional[str] = ""
    company: Optional[str] = ""
    status: CustomerStatus = CustomerStatus.potential
    notes: Optional[str] = ""

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("客户姓名不能为空")
        return v.strip()


class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    company: Optional[str] = None
    status: Optional[CustomerStatus] = None
    notes: Optional[str] = None

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError("客户姓名不能为空")
        return v.strip() if v else v


class CustomerResponse(BaseModel):
    id: int
    name: str
    phone: str
    email: str
    company: str
    status: str
    notes: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CustomerDetailResponse(CustomerResponse):
    follow_ups: List[FollowUpResponse] = []


# ---- Stats Schema ----

class StatusBreakdown(BaseModel):
    potential: int
    interested: int
    closed: int
    lost: int


class StatsResponse(BaseModel):
    total_customers: int
    new_this_month: int
    follow_up_count: int
    status_breakdown: StatusBreakdown

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from database import Base


def now_utc() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    phone = Column(String(50), nullable=True, default="")
    email = Column(String(200), nullable=True, default="")
    company = Column(String(200), nullable=True, default="")
    status = Column(String(20), nullable=False, default="潜在客户")
    notes = Column(Text, nullable=True, default="")
    created_at = Column(DateTime, default=now_utc)
    updated_at = Column(DateTime, default=now_utc, onupdate=now_utc)

    follow_ups = relationship(
        "FollowUp",
        back_populates="customer",
        cascade="all, delete-orphan",
        order_by="FollowUp.created_at.desc()"
    )


class FollowUp(Base):
    __tablename__ = "follow_ups"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    content = Column(Text, nullable=False)
    follow_type = Column(String(20), nullable=False, default="电话")
    created_at = Column(DateTime, default=now_utc)

    customer = relationship("Customer", back_populates="follow_ups")

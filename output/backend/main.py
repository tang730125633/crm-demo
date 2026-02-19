from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from typing import Optional, List
from datetime import datetime, timezone
import os

from database import engine, get_db, Base
from models import Customer, FollowUp
from schemas import (
    CustomerCreate,
    CustomerUpdate,
    CustomerResponse,
    CustomerDetailResponse,
    FollowUpCreate,
    FollowUpResponse,
    StatsResponse,
    StatusBreakdown,
)

# 初始化数据库表
Base.metadata.create_all(bind=engine)

# 启动时自动 seed 示例数据（如果数据库为空）
def auto_seed():
    from database import SessionLocal
    from seed_data import seed
    db = SessionLocal()
    try:
        if db.query(Customer).count() == 0:
            seed(db)
    finally:
        db.close()

auto_seed()

app = FastAPI(title="CRM Demo API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载前端静态文件
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


# ---- 根路径 - 返回前端首页 ----

@app.get("/")
def root():
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "CRM API is running"}


# ---- 客户 CRUD ----

@app.get("/api/customers", response_model=List[CustomerResponse])
def list_customers(
    search: Optional[str] = Query(None, description="按姓名/手机/公司模糊搜索"),
    status: Optional[str] = Query(None, description="按状态筛选"),
    db: Session = Depends(get_db),
):
    query = db.query(Customer)

    if search:
        keyword = f"%{search}%"
        query = query.filter(
            Customer.name.like(keyword)
            | Customer.phone.like(keyword)
            | Customer.company.like(keyword)
        )

    if status:
        query = query.filter(Customer.status == status)

    customers = query.order_by(Customer.created_at.desc()).all()
    return customers


@app.post("/api/customers", response_model=CustomerResponse, status_code=201)
def create_customer(payload: CustomerCreate, db: Session = Depends(get_db)):
    customer = Customer(
        name=payload.name,
        phone=payload.phone or "",
        email=payload.email or "",
        company=payload.company or "",
        status=payload.status.value,
        notes=payload.notes or "",
    )
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer


@app.get("/api/customers/{customer_id}", response_model=CustomerDetailResponse)
def get_customer(customer_id: int, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="客户不存在")
    return customer


@app.put("/api/customers/{customer_id}", response_model=CustomerResponse)
def update_customer(
    customer_id: int,
    payload: CustomerUpdate,
    db: Session = Depends(get_db),
):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="客户不存在")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field == "status" and value is not None:
            value = value.value  # enum -> str
        setattr(customer, field, value)

    customer.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
    db.commit()
    db.refresh(customer)
    return customer


@app.delete("/api/customers/{customer_id}", status_code=204)
def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="客户不存在")
    db.delete(customer)
    db.commit()


# ---- 跟进记录 ----

@app.get("/api/customers/{customer_id}/follow-ups", response_model=List[FollowUpResponse])
def list_follow_ups(customer_id: int, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="客户不存在")

    follow_ups = (
        db.query(FollowUp)
        .filter(FollowUp.customer_id == customer_id)
        .order_by(FollowUp.created_at.desc())
        .all()
    )
    return follow_ups


@app.post(
    "/api/customers/{customer_id}/follow-ups",
    response_model=FollowUpResponse,
    status_code=201,
)
def create_follow_up(
    customer_id: int,
    payload: FollowUpCreate,
    db: Session = Depends(get_db),
):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="客户不存在")

    follow_up = FollowUp(
        customer_id=customer_id,
        content=payload.content,
        follow_type=payload.follow_type.value,
    )
    db.add(follow_up)
    db.commit()
    db.refresh(follow_up)
    return follow_up


@app.delete("/api/follow-ups/{follow_up_id}", status_code=204)
def delete_follow_up(follow_up_id: int, db: Session = Depends(get_db)):
    follow_up = db.query(FollowUp).filter(FollowUp.id == follow_up_id).first()
    if not follow_up:
        raise HTTPException(status_code=404, detail="跟进记录不存在")
    db.delete(follow_up)
    db.commit()


# ---- 统计 ----

@app.get("/api/stats", response_model=StatsResponse)
def get_stats(db: Session = Depends(get_db)):
    now = datetime.now(timezone.utc).replace(tzinfo=None)

    total_customers = db.query(func.count(Customer.id)).scalar() or 0

    new_this_month = (
        db.query(func.count(Customer.id))
        .filter(
            extract("year", Customer.created_at) == now.year,
            extract("month", Customer.created_at) == now.month,
        )
        .scalar()
        or 0
    )

    follow_up_count = db.query(func.count(FollowUp.id)).scalar() or 0

    status_breakdown = StatusBreakdown(
        potential=db.query(func.count(Customer.id)).filter(Customer.status == "潜在客户").scalar() or 0,
        interested=db.query(func.count(Customer.id)).filter(Customer.status == "意向客户").scalar() or 0,
        closed=db.query(func.count(Customer.id)).filter(Customer.status == "成交客户").scalar() or 0,
        lost=db.query(func.count(Customer.id)).filter(Customer.status == "流失客户").scalar() or 0,
    )

    return StatsResponse(
        total_customers=total_customers,
        new_this_month=new_this_month,
        follow_up_count=follow_up_count,
        status_breakdown=status_breakdown,
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

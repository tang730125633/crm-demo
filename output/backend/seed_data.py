"""
seed_data.py - 初始化示例数据脚本
运行方式: python seed_data.py
"""
import sys
import os

# 保证能找到同目录下的其他模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import engine, SessionLocal, Base
from models import Customer, FollowUp
from datetime import datetime, timedelta, timezone


def now_offset(days: int = 0) -> datetime:
    return (datetime.now(timezone.utc) - timedelta(days=days)).replace(tzinfo=None)


CUSTOMERS = [
    {
        "name": "张伟",
        "phone": "13800138001",
        "email": "zhangwei@example.com",
        "company": "北京科技有限公司",
        "status": "成交客户",
        "notes": "重点客户，已签年度合同",
        "days_ago": 90,
    },
    {
        "name": "李娜",
        "phone": "13900139002",
        "email": "lina@example.com",
        "company": "上海贸易集团",
        "status": "意向客户",
        "notes": "需要下周再跟进确认预算",
        "days_ago": 30,
    },
    {
        "name": "王芳",
        "phone": "13700137003",
        "email": "wangfang@example.com",
        "company": "广州创新科技",
        "status": "潜在客户",
        "notes": "通过展会获取的名片",
        "days_ago": 10,
    },
    {
        "name": "刘洋",
        "phone": "13600136004",
        "email": "liuyang@example.com",
        "company": "深圳互联网公司",
        "status": "意向客户",
        "notes": "正在评估竞品，需跟进",
        "days_ago": 20,
    },
    {
        "name": "陈静",
        "phone": "13500135005",
        "email": "chenjing@example.com",
        "company": "杭州电商平台",
        "status": "流失客户",
        "notes": "选择了竞品，记录备案",
        "days_ago": 60,
    },
    {
        "name": "赵磊",
        "phone": "13400134006",
        "email": "zhaolei@example.com",
        "company": "成都软件开发",
        "status": "成交客户",
        "notes": "已完成首次交付，客户满意",
        "days_ago": 45,
    },
    {
        "name": "黄丽",
        "phone": "13300133007",
        "email": "huangli@example.com",
        "company": "武汉制造业集团",
        "status": "潜在客户",
        "notes": "朋友介绍，有数字化转型需求",
        "days_ago": 5,
    },
    {
        "name": "周建国",
        "phone": "13200132008",
        "email": "zhoujg@example.com",
        "company": "南京物流公司",
        "status": "意向客户",
        "notes": "需要定制化方案，已发送初步报价",
        "days_ago": 15,
    },
    {
        "name": "吴雪",
        "phone": "13100131009",
        "email": "wuxue@example.com",
        "company": "西安教育科技",
        "status": "潜在客户",
        "notes": "通过官网留资，等待首次沟通",
        "days_ago": 3,
    },
    {
        "name": "孙明",
        "phone": "13000130010",
        "email": "sunming@example.com",
        "company": "重庆汽车配件",
        "status": "成交客户",
        "notes": "老客户，续签第三年合同",
        "days_ago": 120,
    },
]

FOLLOW_UPS = [
    # 张伟 (customer index 0)
    {"customer_idx": 0, "content": "电话确认合同条款，客户同意签署", "follow_type": "电话", "days_ago": 85},
    {"customer_idx": 0, "content": "微信发送合同电子版，等待回签", "follow_type": "微信", "days_ago": 83},
    {"customer_idx": 0, "content": "上门拜访，完成正式签约", "follow_type": "拜访", "days_ago": 80},
    # 李娜 (customer index 1)
    {"customer_idx": 1, "content": "首次电话沟通，了解需求，客户表示有兴趣", "follow_type": "电话", "days_ago": 28},
    {"customer_idx": 1, "content": "发送产品介绍和报价单", "follow_type": "邮件", "days_ago": 25},
    {"customer_idx": 1, "content": "微信跟进，客户说本月预算已用完，下月再定", "follow_type": "微信", "days_ago": 10},
    # 刘洋 (customer index 3)
    {"customer_idx": 3, "content": "电话联系，确认客户正在对比3家供应商", "follow_type": "电话", "days_ago": 18},
    {"customer_idx": 3, "content": "发送竞品对比分析报告", "follow_type": "邮件", "days_ago": 15},
    # 赵磊 (customer index 5)
    {"customer_idx": 5, "content": "首次上门拜访，演示产品，客户反馈正面", "follow_type": "拜访", "days_ago": 43},
    {"customer_idx": 5, "content": "电话确认交付时间表", "follow_type": "电话", "days_ago": 40},
    {"customer_idx": 5, "content": "项目交付，收集客户反馈", "follow_type": "拜访", "days_ago": 35},
    # 周建国 (customer index 7)
    {"customer_idx": 7, "content": "收到客户询价，电话初步沟通需求", "follow_type": "电话", "days_ago": 14},
    {"customer_idx": 7, "content": "邮件发送定制化方案及报价", "follow_type": "邮件", "days_ago": 12},
    # 孙明 (customer index 9)
    {"customer_idx": 9, "content": "电话提醒合同到期，询问续约意向", "follow_type": "电话", "days_ago": 115},
    {"customer_idx": 9, "content": "上门拜访，确认续签第三年合同", "follow_type": "拜访", "days_ago": 110},
    {"customer_idx": 9, "content": "完成续签，微信发送合同副本", "follow_type": "微信", "days_ago": 108},
]


def seed(db=None):
    """初始化示例数据。可传入已有 db session，也可独立运行。"""
    Base.metadata.create_all(bind=engine)
    own_db = db is None
    if own_db:
        db = SessionLocal()

    try:
        existing = db.query(Customer).count()
        if existing > 0:
            print(f"数据库已有 {existing} 条客户记录，跳过初始化。")
            return

        customers = []
        for data in CUSTOMERS:
            created = now_offset(data["days_ago"])
            c = Customer(
                name=data["name"],
                phone=data["phone"],
                email=data["email"],
                company=data["company"],
                status=data["status"],
                notes=data["notes"],
                created_at=created,
                updated_at=created,
            )
            db.add(c)
            customers.append(c)

        db.flush()

        for fu_data in FOLLOW_UPS:
            customer = customers[fu_data["customer_idx"]]
            fu = FollowUp(
                customer_id=customer.id,
                content=fu_data["content"],
                follow_type=fu_data["follow_type"],
                created_at=now_offset(fu_data["days_ago"]),
            )
            db.add(fu)

        db.commit()
        print(f"初始化成功: {len(CUSTOMERS)} 条客户，{len(FOLLOW_UPS)} 条跟进记录")

    except Exception as e:
        db.rollback()
        print(f"初始化失败: {e}")
        raise
    finally:
        if own_db:
            db.close()


if __name__ == "__main__":
    seed()

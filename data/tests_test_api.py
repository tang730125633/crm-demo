"""
CRM Demo API Tests
Covers all 10 endpoints: health check, stats, customer CRUD, follow-up CRUD.
Run with: pytest data/tests_test_api.py -v (from project root)
or after moving to output/tests/: pytest output/tests/test_api.py -v
"""
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Path setup - works when file is in data/ or output/tests/
# ---------------------------------------------------------------------------
_this_dir = Path(__file__).parent
# If file is in data/, backend is at ../output/backend
# If file is in output/tests/, backend is at ../backend
_backend_candidate_1 = _this_dir.parent / "output" / "backend"
_backend_candidate_2 = _this_dir.parent / "backend"
if _backend_candidate_1.exists():
    sys.path.insert(0, str(_backend_candidate_1))
elif _backend_candidate_2.exists():
    sys.path.insert(0, str(_backend_candidate_2))

import pytest

# ---------------------------------------------------------------------------
# Helpers / shared data
# ---------------------------------------------------------------------------

CUSTOMER_PAYLOAD = {
    "name": "张三",
    "phone": "13800138000",
    "email": "zhangsan@example.com",
    "company": "ABC科技",
    "status": "潜在客户",
    "notes": "测试备注",
}

FOLLOW_UP_PAYLOAD = {
    "content": "第一次电话沟通，客户有意向",
    "follow_type": "电话",
}


def create_customer(client, payload=None):
    """Helper: create a customer and return the response JSON."""
    data = payload or CUSTOMER_PAYLOAD
    resp = client.post("/api/customers", json=data)
    assert resp.status_code == 201
    return resp.json()


def create_follow_up(client, customer_id, payload=None):
    """Helper: create a follow-up for a customer and return the response JSON."""
    data = payload or FOLLOW_UP_PAYLOAD
    resp = client.post(f"/api/customers/{customer_id}/follow-ups", json=data)
    assert resp.status_code == 201
    return resp.json()


# ===========================================================================
# 1. GET / - Health check
# ===========================================================================

class TestRootEndpoint:
    def test_health_check_returns_200(self, client):
        resp = client.get("/")
        assert resp.status_code == 200

    def test_health_check_message(self, client):
        resp = client.get("/")
        data = resp.json()
        assert "message" in data
        assert "running" in data["message"].lower() or "crm" in data["message"].lower()


# ===========================================================================
# 2. GET /api/stats - Statistics
# ===========================================================================

class TestStatsEndpoint:
    def test_stats_returns_200_on_empty_db(self, client):
        resp = client.get("/api/stats")
        assert resp.status_code == 200

    def test_stats_structure(self, client):
        resp = client.get("/api/stats")
        data = resp.json()
        assert "total_customers" in data
        assert "new_this_month" in data
        assert "follow_up_count" in data
        assert "status_breakdown" in data

    def test_stats_zeros_on_empty_db(self, client):
        resp = client.get("/api/stats")
        data = resp.json()
        assert data["total_customers"] == 0
        assert data["follow_up_count"] == 0

    def test_stats_counts_after_creating_customer(self, client):
        create_customer(client)
        resp = client.get("/api/stats")
        data = resp.json()
        assert data["total_customers"] == 1
        assert data["new_this_month"] == 1

    def test_stats_status_breakdown_structure(self, client):
        resp = client.get("/api/stats")
        breakdown = resp.json()["status_breakdown"]
        assert "potential" in breakdown
        assert "interested" in breakdown
        assert "closed" in breakdown
        assert "lost" in breakdown

    def test_stats_follow_up_count_increments(self, client):
        customer = create_customer(client)
        create_follow_up(client, customer["id"])
        resp = client.get("/api/stats")
        data = resp.json()
        assert data["follow_up_count"] == 1


# ===========================================================================
# 3. POST /api/customers - Create customer
# ===========================================================================

class TestCreateCustomer:
    def test_create_customer_success(self, client):
        resp = client.post("/api/customers", json=CUSTOMER_PAYLOAD)
        assert resp.status_code == 201

    def test_create_customer_returns_id(self, client):
        resp = client.post("/api/customers", json=CUSTOMER_PAYLOAD)
        data = resp.json()
        assert "id" in data
        assert isinstance(data["id"], int)

    def test_create_customer_name_persisted(self, client):
        resp = client.post("/api/customers", json=CUSTOMER_PAYLOAD)
        assert resp.json()["name"] == "张三"

    def test_create_customer_status_defaults_to_potential(self, client):
        resp = client.post("/api/customers", json={"name": "李四"})
        assert resp.status_code == 201
        assert resp.json()["status"] == "潜在客户"

    def test_create_customer_with_all_statuses(self, client):
        for status in ["潜在客户", "意向客户", "成交客户", "流失客户"]:
            resp = client.post("/api/customers", json={"name": "测试", "status": status})
            assert resp.status_code == 201, f"Failed for status: {status}"
            assert resp.json()["status"] == status

    def test_create_customer_missing_name_returns_422(self, client):
        resp = client.post("/api/customers", json={"phone": "13800138000"})
        assert resp.status_code == 422

    def test_create_customer_empty_name_returns_422(self, client):
        resp = client.post("/api/customers", json={"name": "   "})
        assert resp.status_code == 422

    def test_create_customer_invalid_status_returns_422(self, client):
        resp = client.post("/api/customers", json={"name": "王五", "status": "无效状态"})
        assert resp.status_code == 422

    def test_create_customer_optional_fields_default_empty(self, client):
        resp = client.post("/api/customers", json={"name": "极简客户"})
        data = resp.json()
        assert data["phone"] == ""
        assert data["email"] == ""
        assert data["company"] == ""


# ===========================================================================
# 4. GET /api/customers - List customers
# ===========================================================================

class TestListCustomers:
    def test_list_customers_empty(self, client):
        resp = client.get("/api/customers")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_list_customers_returns_created(self, client):
        create_customer(client)
        resp = client.get("/api/customers")
        assert len(resp.json()) == 1

    def test_list_customers_multiple(self, client):
        create_customer(client, {"name": "客户A"})
        create_customer(client, {"name": "客户B"})
        resp = client.get("/api/customers")
        assert len(resp.json()) == 2

    def test_list_customers_search_by_name(self, client):
        create_customer(client, {"name": "张三"})
        create_customer(client, {"name": "李四"})
        resp = client.get("/api/customers?search=张三")
        data = resp.json()
        assert len(data) == 1
        assert data[0]["name"] == "张三"

    def test_list_customers_search_by_company(self, client):
        create_customer(client, {"name": "甲", "company": "ABC科技"})
        create_customer(client, {"name": "乙", "company": "XYZ公司"})
        resp = client.get("/api/customers?search=ABC")
        data = resp.json()
        assert len(data) == 1
        assert data[0]["company"] == "ABC科技"

    def test_list_customers_search_by_phone(self, client):
        create_customer(client, {"name": "甲", "phone": "13800138000"})
        create_customer(client, {"name": "乙", "phone": "18600000000"})
        resp = client.get("/api/customers?search=138001")
        data = resp.json()
        assert len(data) == 1

    def test_list_customers_filter_by_status(self, client):
        create_customer(client, {"name": "甲", "status": "潜在客户"})
        create_customer(client, {"name": "乙", "status": "成交客户"})
        resp = client.get("/api/customers?status=成交客户")
        data = resp.json()
        assert len(data) == 1
        assert data[0]["status"] == "成交客户"

    def test_list_customers_search_no_match_returns_empty(self, client):
        create_customer(client)
        resp = client.get("/api/customers?search=不存在的关键词XYZ")
        assert resp.json() == []


# ===========================================================================
# 5. GET /api/customers/{id} - Get single customer
# ===========================================================================

class TestGetCustomer:
    def test_get_customer_success(self, client):
        customer = create_customer(client)
        resp = client.get(f"/api/customers/{customer['id']}")
        assert resp.status_code == 200

    def test_get_customer_returns_correct_data(self, client):
        customer = create_customer(client)
        resp = client.get(f"/api/customers/{customer['id']}")
        data = resp.json()
        assert data["name"] == "张三"
        assert data["id"] == customer["id"]

    def test_get_customer_includes_follow_ups_field(self, client):
        customer = create_customer(client)
        resp = client.get(f"/api/customers/{customer['id']}")
        data = resp.json()
        assert "follow_ups" in data
        assert isinstance(data["follow_ups"], list)

    def test_get_customer_not_found_returns_404(self, client):
        resp = client.get("/api/customers/99999")
        assert resp.status_code == 404

    def test_get_customer_invalid_id_returns_422(self, client):
        resp = client.get("/api/customers/abc")
        assert resp.status_code == 422


# ===========================================================================
# 6. PUT /api/customers/{id} - Update customer
# ===========================================================================

class TestUpdateCustomer:
    def test_update_customer_name(self, client):
        customer = create_customer(client)
        resp = client.put(f"/api/customers/{customer['id']}", json={"name": "张三新名"})
        assert resp.status_code == 200
        assert resp.json()["name"] == "张三新名"

    def test_update_customer_status(self, client):
        customer = create_customer(client)
        resp = client.put(f"/api/customers/{customer['id']}", json={"status": "成交客户"})
        assert resp.status_code == 200
        assert resp.json()["status"] == "成交客户"

    def test_update_customer_partial_update(self, client):
        customer = create_customer(client)
        resp = client.put(
            f"/api/customers/{customer['id']}",
            json={"notes": "更新了备注"}
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["notes"] == "更新了备注"
        assert data["name"] == "张三"  # unchanged

    def test_update_customer_not_found_returns_404(self, client):
        resp = client.put("/api/customers/99999", json={"name": "不存在"})
        assert resp.status_code == 404

    def test_update_customer_empty_name_returns_422(self, client):
        customer = create_customer(client)
        resp = client.put(f"/api/customers/{customer['id']}", json={"name": "  "})
        assert resp.status_code == 422

    def test_update_customer_invalid_status_returns_422(self, client):
        customer = create_customer(client)
        resp = client.put(
            f"/api/customers/{customer['id']}",
            json={"status": "不合法状态"}
        )
        assert resp.status_code == 422


# ===========================================================================
# 7. POST /api/customers/{id}/follow-ups - Create follow-up
# ===========================================================================

class TestCreateFollowUp:
    def test_create_follow_up_success(self, client):
        customer = create_customer(client)
        resp = client.post(
            f"/api/customers/{customer['id']}/follow-ups",
            json=FOLLOW_UP_PAYLOAD
        )
        assert resp.status_code == 201

    def test_create_follow_up_returns_id(self, client):
        customer = create_customer(client)
        follow_up = create_follow_up(client, customer["id"])
        assert "id" in follow_up
        assert follow_up["customer_id"] == customer["id"]

    def test_create_follow_up_content_persisted(self, client):
        customer = create_customer(client)
        follow_up = create_follow_up(client, customer["id"])
        assert follow_up["content"] == FOLLOW_UP_PAYLOAD["content"]

    def test_create_follow_up_all_types(self, client):
        customer = create_customer(client)
        for ftype in ["电话", "微信", "拜访", "邮件"]:
            resp = client.post(
                f"/api/customers/{customer['id']}/follow-ups",
                json={"content": "沟通记录", "follow_type": ftype}
            )
            assert resp.status_code == 201, f"Failed for follow_type: {ftype}"
            assert resp.json()["follow_type"] == ftype

    def test_create_follow_up_default_type_is_phone(self, client):
        customer = create_customer(client)
        resp = client.post(
            f"/api/customers/{customer['id']}/follow-ups",
            json={"content": "仅内容"}
        )
        assert resp.status_code == 201
        assert resp.json()["follow_type"] == "电话"

    def test_create_follow_up_empty_content_returns_422(self, client):
        customer = create_customer(client)
        resp = client.post(
            f"/api/customers/{customer['id']}/follow-ups",
            json={"content": "   ", "follow_type": "电话"}
        )
        assert resp.status_code == 422

    def test_create_follow_up_missing_content_returns_422(self, client):
        customer = create_customer(client)
        resp = client.post(
            f"/api/customers/{customer['id']}/follow-ups",
            json={"follow_type": "电话"}
        )
        assert resp.status_code == 422

    def test_create_follow_up_customer_not_found_returns_404(self, client):
        resp = client.post(
            "/api/customers/99999/follow-ups",
            json=FOLLOW_UP_PAYLOAD
        )
        assert resp.status_code == 404

    def test_create_follow_up_invalid_type_returns_422(self, client):
        customer = create_customer(client)
        resp = client.post(
            f"/api/customers/{customer['id']}/follow-ups",
            json={"content": "内容", "follow_type": "传真"}
        )
        assert resp.status_code == 422


# ===========================================================================
# 8. GET /api/customers/{id}/follow-ups - List follow-ups
# ===========================================================================

class TestListFollowUps:
    def test_list_follow_ups_empty(self, client):
        customer = create_customer(client)
        resp = client.get(f"/api/customers/{customer['id']}/follow-ups")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_list_follow_ups_returns_created(self, client):
        customer = create_customer(client)
        create_follow_up(client, customer["id"])
        resp = client.get(f"/api/customers/{customer['id']}/follow-ups")
        data = resp.json()
        assert len(data) == 1

    def test_list_follow_ups_multiple(self, client):
        customer = create_customer(client)
        create_follow_up(client, customer["id"], {"content": "第一次", "follow_type": "电话"})
        create_follow_up(client, customer["id"], {"content": "第二次", "follow_type": "微信"})
        resp = client.get(f"/api/customers/{customer['id']}/follow-ups")
        assert len(resp.json()) == 2

    def test_list_follow_ups_customer_not_found_returns_404(self, client):
        resp = client.get("/api/customers/99999/follow-ups")
        assert resp.status_code == 404

    def test_follow_ups_appear_in_customer_detail(self, client):
        customer = create_customer(client)
        create_follow_up(client, customer["id"])
        detail = client.get(f"/api/customers/{customer['id']}").json()
        assert len(detail["follow_ups"]) == 1


# ===========================================================================
# 9. DELETE /api/follow-ups/{id} - Delete follow-up
# ===========================================================================

class TestDeleteFollowUp:
    def test_delete_follow_up_success(self, client):
        customer = create_customer(client)
        follow_up = create_follow_up(client, customer["id"])
        resp = client.delete(f"/api/follow-ups/{follow_up['id']}")
        assert resp.status_code == 204

    def test_delete_follow_up_is_actually_removed(self, client):
        customer = create_customer(client)
        follow_up = create_follow_up(client, customer["id"])
        client.delete(f"/api/follow-ups/{follow_up['id']}")
        resp = client.get(f"/api/customers/{customer['id']}/follow-ups")
        assert resp.json() == []

    def test_delete_follow_up_not_found_returns_404(self, client):
        resp = client.delete("/api/follow-ups/99999")
        assert resp.status_code == 404

    def test_delete_follow_up_twice_returns_404(self, client):
        customer = create_customer(client)
        follow_up = create_follow_up(client, customer["id"])
        client.delete(f"/api/follow-ups/{follow_up['id']}")
        resp = client.delete(f"/api/follow-ups/{follow_up['id']}")
        assert resp.status_code == 404


# ===========================================================================
# 10. DELETE /api/customers/{id} - Delete customer
# ===========================================================================

class TestDeleteCustomer:
    def test_delete_customer_success(self, client):
        customer = create_customer(client)
        resp = client.delete(f"/api/customers/{customer['id']}")
        assert resp.status_code == 204

    def test_delete_customer_is_actually_removed(self, client):
        customer = create_customer(client)
        client.delete(f"/api/customers/{customer['id']}")
        resp = client.get(f"/api/customers/{customer['id']}")
        assert resp.status_code == 404

    def test_delete_customer_no_longer_in_list(self, client):
        customer = create_customer(client)
        client.delete(f"/api/customers/{customer['id']}")
        resp = client.get("/api/customers")
        assert resp.json() == []

    def test_delete_customer_not_found_returns_404(self, client):
        resp = client.delete("/api/customers/99999")
        assert resp.status_code == 404

    def test_delete_customer_also_deletes_follow_ups(self, client):
        """Cascade delete: removing a customer removes their follow-up records."""
        customer = create_customer(client)
        create_follow_up(client, customer["id"])
        client.delete(f"/api/customers/{customer['id']}")
        # Stats follow_up_count should drop back to 0
        stats = client.get("/api/stats").json()
        assert stats["follow_up_count"] == 0

    def test_delete_customer_twice_returns_404(self, client):
        customer = create_customer(client)
        client.delete(f"/api/customers/{customer['id']}")
        resp = client.delete(f"/api/customers/{customer['id']}")
        assert resp.status_code == 404

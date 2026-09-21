import json
import sys
import pytest

T = {"start_price": 11, "start_include_km": 3, "per_km": 2.5, "per_slow_min": 0.8, "night_factor": 1.2}

@pytest.fixture
def service_cls(tmp_path, monkeypatch):
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    for name in list(sys.modules):
        if name.startswith("app"):
            del sys.modules[name]
    from app import seed
    from app.services.taxi_service import TaxiService
    seed.init_db()
    return TaxiService

def _count(s):
    return s._c.execute("SELECT COUNT(*) c FROM calc_runs").fetchone()["c"]

def test_preview_does_not_add_rows(service_cls):
    with service_cls() as s:
        rid = s.fare(5, 2, False, None, True)["run_id"]
        before = _count(s)
        p1 = s.reverse(rid, 6.0, None, True)
        p2 = s.reverse(rid, 7.0, 3.0, True)
        assert _count(s) == before
        assert p1["run_id"] is None and p2["run_id"] is None
        assert p1["reversal_of"] == rid

def test_commit_writes_new_row_and_marks_original(service_cls):
    with service_cls() as s:
        r0 = s.fare(5, 2, False, None, True)
        rid = r0["run_id"]
        before = _count(s)
        out = s.reverse(rid, 6.0, None, False)
        assert _count(s) == before + 1
        new_id = out["run_id"]
        assert new_id != rid and out["reversal_of"] == rid
        from app.repositories import runs
        old, new = runs.get(s._c, rid), runs.get(s._c, new_id)
        assert old["reversed_by"] == new_id
        assert new["reversal_of"] == rid
        assert json.loads(new["result_json"])["total"] == out["total"]
        assert out["distance_km"] == 6.0 and out["slow_min"] == 2.0

def test_already_reversed_cannot_reverse_again(service_cls):
    with service_cls() as s:
        rid = s.fare(5, 2, False, None, True)["run_id"]
        s.reverse(rid, 6.0, None, False)
        from app.services.taxi_service import ReversalError
        with pytest.raises(ReversalError) as e:
            s.reverse(rid, 7.0, None, False)
        assert e.value.status_code == 409

def test_requires_new_km_or_slow(service_cls):
    with service_cls() as s:
        rid = s.fare(5, 2, False, None, True)["run_id"]
        from app.services.taxi_service import ReversalError
        with pytest.raises(ReversalError) as e:
            s.reverse(rid, None, None, False)
        assert e.value.status_code == 400

def test_reverse_uses_current_tariff(service_cls):
    with service_cls() as s:
        rid = s.fare(5, 2, False, None, True)["run_id"]
        s._c.execute("UPDATE tariff SET per_km=3.0 WHERE id=(SELECT id FROM tariff LIMIT 1)")
        s._c.commit()
        out = s.reverse(rid, 5.0, None, False)
        # 5 公里：起步 11 + 2 公里 * 3.0 + 低速 2 * 0.8 = 18.6
        assert out["mileage"] == 6.0
        assert out["total"] == 18.6

def test_commit_keeps_original_breakdown_unchanged(service_cls):
    with service_cls() as s:
        rid = s.fare(5, 2, False, None, True)["run_id"]
        from app.repositories import runs
        before = runs.get(s._c, rid)
        before_result = json.loads(before["result_json"])
        before_cnt = _count(s)

        out = s.reverse(rid, 6.0, None, False)
        assert _count(s) == before_cnt + 1

        old = runs.get(s._c, rid)
        new = runs.get(s._c, out["run_id"])
        # 原记录拆解保持冲正前写入时的值，不被新记录那一套覆盖
        assert json.loads(old["result_json"]) == before_result
        assert json.loads(old["result_json"])["start"] == before_result["start"]
        assert json.loads(old["result_json"])["mileage"] == before_result["mileage"]
        assert json.loads(old["result_json"])["total"] == before_result["total"]
        # 新记录确实是冲正后的一套，且记下原编号
        assert json.loads(new["result_json"])["total"] == out["total"]
        assert new["reversal_of"] == rid
        assert old["reversed_by"] == out["run_id"]
        # 新旧拆解确实不同，保证断言有意义
        assert json.loads(new["result_json"])["mileage"] != before_result["mileage"]

def test_compare_cannot_reverse_commit(service_cls):
    with service_cls() as s:
        cid = s.compare(8, 3, True)["run_id"]
        before = _count(s)
        from app.services.taxi_service import ReversalError
        with pytest.raises(ReversalError) as e:
            s.reverse(cid, 9.0, None, False)
        assert e.value.status_code == 400
        # 没有写出任何新记录
        assert _count(s) == before
        from app.repositories import runs
        row = runs.get(s._c, cid)
        assert row["kind"] == "compare" and row["reversed_by"] is None

def test_compare_cannot_reverse_preview(service_cls):
    with service_cls() as s:
        cid = s.compare(8, 3, True)["run_id"]
        before = _count(s)
        from app.services.taxi_service import ReversalError
        with pytest.raises(ReversalError) as e:
            s.reverse(cid, 9.0, None, True)
        assert e.value.status_code == 400
        assert _count(s) == before

def test_missing_run_404(service_cls):
    with service_cls() as s:
        from app.services.taxi_service import ReversalError
        with pytest.raises(ReversalError) as e:
            s.reverse(9999, 6.0, None, False)
        assert e.value.status_code == 404

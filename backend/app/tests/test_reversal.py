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

def test_compare_run_cannot_reverse(service_cls):
    with service_cls() as s:
        rid = s.compare(5, 2, True)["run_id"]
        before = _count(s)
        from app.services.taxi_service import ReversalError
        # 提交与预览都不允许，且不得写出新记录
        for preview in (False, True):
            with pytest.raises(ReversalError) as e:
                s.reverse(rid, 6.0, None, preview)
            assert e.value.status_code == 400
        assert _count(s) == before

def test_original_breakdown_preserved_after_commit(service_cls):
    with service_cls() as s:
        r0 = s.fare(5, 2, False, None, True)
        rid = r0["run_id"]
        out = s.reverse(rid, 8.0, None, False)
        from app.repositories import runs
        old_result = json.loads(runs.get(s._c, rid)["result_json"])
        # 原记录的起步、里程、应付仍是冲正前写入时的那一版
        assert old_result["start"] == r0["start"]
        assert old_result["mileage"] == r0["mileage"]
        assert old_result["total"] == r0["total"]
        assert out["total"] != r0["total"]
        # 新记录才是冲正后那一套
        new_result = json.loads(runs.get(s._c, out["run_id"])["result_json"])
        assert new_result["mileage"] == out["mileage"]
        assert new_result["total"] == out["total"]

def test_already_reversed_cannot_preview_again(service_cls):
    with service_cls() as s:
        rid = s.fare(5, 2, False, None, True)["run_id"]
        s.reverse(rid, 6.0, None, False)
        before = _count(s)
        from app.services.taxi_service import ReversalError
        with pytest.raises(ReversalError) as e:
            s.reverse(rid, 7.0, None, True)
        assert e.value.status_code == 409
        assert _count(s) == before

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

def test_missing_run_404(service_cls):
    with service_cls() as s:
        from app.services.taxi_service import ReversalError
        with pytest.raises(ReversalError) as e:
            s.reverse(9999, 6.0, None, False)
        assert e.value.status_code == 404

import json
from app.db import connect
from app.engines.night_compare import compare_day_night
from app.engines.tariff_breakdown import calc_fare
from app.repositories import runs, settings, tariff, trips

class ReversalError(Exception):
    def __init__(self, status_code: int, detail: str):
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail

class TaxiService:
    def __init__(self): self._c = connect()
    def close(self): self._c.close()
    def __enter__(self): return self
    def __exit__(self, *a): self.close()
    def list_trips(self): return trips.list_all(self._c)
    def trip(self, tid): return trips.get(self._c, tid)
    def tariff(self): return tariff.get_active(self._c)
    def settings(self): return settings.get_map(self._c)
    def history(self, limit=50):
        items = runs.list_recent(self._c, limit)
        for it in items:
            it["input"] = json.loads(it["input_json"])
            it["result"] = json.loads(it["result_json"])
        return items
    def fare(self, distance_km, slow_min, night, trip_id, persist):
        t = tariff.get_active(self._c)
        r = calc_fare(distance_km, slow_min, night, t)
        rid = runs.insert(self._c, "fare", {"distance_km": distance_km, "slow_min": slow_min, "night": night}, r, trip_id) if persist else None
        return {"run_id": rid, **r}
    def compare(self, distance_km, slow_min, persist):
        t = tariff.get_active(self._c)
        r = compare_day_night(distance_km, slow_min, t)
        rid = runs.insert(self._c, "compare", {"distance_km": distance_km, "slow_min": slow_min}, r, None) if persist else None
        return {"run_id": rid, **r}
    def reverse(self, run_id, distance_km, slow_min, preview):
        """对一条有效 fare 记录按当前运价冲正：预览不落库；提交另写新记录并标记原记录。"""
        orig = runs.get(self._c, run_id)
        if not orig:
            raise ReversalError(404, "记录不存在")
        if orig["kind"] != "fare":
            raise ReversalError(400, "compare 记录不能冲正")
        if orig["reversed_by"] is not None:
            raise ReversalError(409, "该记录已被冲正，不能再次冲正")
        if distance_km is None and slow_min is None:
            raise ReversalError(400, "必须给出新的公里或新的低速")
        orig_input = json.loads(orig["input_json"])
        new_km = float(distance_km) if distance_km is not None else float(orig_input["distance_km"])
        new_slow = float(slow_min) if slow_min is not None else float(orig_input["slow_min"])
        night = bool(orig_input.get("night", False))
        t = tariff.get_active(self._c)
        r = calc_fare(new_km, new_slow, night, t)
        payload = {"distance_km": new_km, "slow_min": new_slow, "night": night}
        if preview:
            return {"preview": True, "run_id": None, "reversal_of": run_id, **r}
        new_id = runs.insert_reversal(self._c, payload, r, run_id, orig["trip_id"])
        return {"preview": False, "run_id": new_id, "reversal_of": run_id, **r}
    def dashboard(self):
        items = trips.list_all(self._c)
        clean = [x for x in items if "种子" not in x["label"]]
        dirty = [x for x in items if "种子" in x["label"]]
        return {"trip_count": len(items), "clean": len(clean), "dirty": len(dirty)}

from pydantic import BaseModel, Field

class FareRequest(BaseModel):
    distance_km: float = Field(ge=0)
    slow_min: float = Field(ge=0)
    night: bool = False
    trip_id: int | None = None
    persist: bool = True

class CompareRequest(BaseModel):
    distance_km: float = Field(ge=0)
    slow_min: float = Field(ge=0)
    persist: bool = False

class ReverseRequest(BaseModel):
    # 新公里 / 新低至少给出一个，缺省项沿用原记录
    distance_km: float | None = Field(default=None, ge=0)
    slow_min: float | None = Field(default=None, ge=0)
    preview: bool = False

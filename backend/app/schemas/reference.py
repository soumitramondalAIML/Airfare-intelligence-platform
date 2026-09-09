from pydantic import BaseModel, ConfigDict


class RouteResponse(BaseModel):
    id: int
    origin: str
    destination: str
    weight: float
    active: bool

    model_config = ConfigDict(from_attributes=True)


class CarrierResponse(BaseModel):
    id: int
    code: str
    name: str
    active: bool

    model_config = ConfigDict(from_attributes=True)


class DataSourceResponse(BaseModel):
    id: int
    code: str
    name: str
    source_type: str
    base_url: str | None
    active: bool

    model_config = ConfigDict(from_attributes=True)


class AdvanceWindowsResponse(BaseModel):
    windows: list[int]
from pydantic import BaseModel, Field
from typing import Optional

class ScenarioIn(BaseModel):
    tiempo: float = Field(..., gt=0)
    costo_hora: float = Field(..., gt=0)
    riesgo: float = Field(0, ge=0, le=1)

class ScenarioOut(ScenarioIn):
    costo_total: float

class ResultRow(BaseModel):
    id: int
    tiempo: float
    costo_hora: float
    riesgo: float
    costo_total: float
    created_at: Optional[str] = None


class Result(BaseModel):
    id: int
    tiempo: float
    costo_hora: float
    riesgo: float
    costo_total: float


class FinalResult(BaseModel):
    id: int
    tiempo_promedio: float
    costo_promedio: float
    riesgo_promedio: float
    created_at: Optional[str] = None


from pydantic import BaseModel, Field
from typing import Optional


# -----------------------------
# 🟦 REQUEST INPUT
# -----------------------------
class ScenarioIn(BaseModel):
    tiempo: float = Field(..., gt=0)
    costo_hora: float = Field(..., gt=0)
    riesgo: float = Field(0, ge=0, le=1)


# -----------------------------
# 🟩 RESPONSE OUTPUT
# -----------------------------
class ScenarioOut(ScenarioIn):
    costo_total: float


# -----------------------------
# 🟨 ROW FROM "resultados"
# -----------------------------
class ResultRow(BaseModel):
    id: int
    tiempo: float
    costo_hora: float
    riesgo: float
    costo_total: float
    created_at: Optional[str] = None


# -----------------------------
# 🟧 ROW FROM "resultados_finales"
# -----------------------------
class FinalResult(BaseModel):
    id: int
    tiempo_promedio: float
    costo_promedio: float
    riesgo_promedio: float
    created_at: Optional[str] = None

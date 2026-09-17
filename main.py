from fastapi import FastAPI
from datetime import date
from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime
from fastapi import status
from fastapi import HTTPException, status


class TransactionType(str, Enum):
    income = "income"
    expense = "expense"


class TransactionCreate(BaseModel):
    amount: float = Field(gt=0)
    type: TransactionType
    category: str = Field(min_length=1, max_length=50)
    description: str | None = Field(default=None, max_length=200)
    occurred_on: date

class TransactionOut(BaseModel):
    id: int
    amount: float
    type: TransactionType
    category: str
    description: str | None
    occurred_on: date
    created_at: datetime

app = FastAPI()
# ── 임시 저장소 (8장에서 진짜 DB로 교체한다) ──────────────
fake_db: list[dict] = []   # 거래 기록을 담아 둘 리스트
_next_id = 1                # 다음에 부여할 id. 저장할 때마다 1씩 늘린다


def _find(transaction_id: int):
    """id로 거래 하나를 찾는다. 없으면 None을 돌려준다."""
    return next((r for r in fake_db if r["id"] == transaction_id), None)

@app.get("/")
def read_root():
    return {"message": "지출 관리 API에 오신 것을 환영합니다"}


@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/transactions/{transaction_id}", response_model=TransactionOut)
def get_transaction(transaction_id: int):
    row = _find(transaction_id)
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{transaction_id}번 거래를 찾을 수 없습니다",
        )
    return row

@app.get("/transactions")
def list_transactions(skip: int = 0, limit: int = 10, type: str | None = None):
    return {"skip": skip, "limit": limit, "type": type}


@app.post("/transactions", response_model=TransactionOut, status_code=status.HTTP_201_CREATED)
def create_transaction(payload: TransactionCreate):
    global _next_id
    record = {"id": _next_id, "created_at": datetime.now(), **payload.model_dump()}
    fake_db.append(record)   # ★ 저장소에 담는다
    _next_id += 1            # 다음 id 준비
    return record
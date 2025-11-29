# backend/app/schemas.py

from pydantic import BaseModel
from typing import Optional, Dict


class ProposeRequest(BaseModel):
    prompt: str


class ConfirmRequest(BaseModel):
    event: Dict
    token_dict: Optional[Dict] = None

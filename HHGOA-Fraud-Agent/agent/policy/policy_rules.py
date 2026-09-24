"""Policy Rules enumeration and metadata according to Fraud Policy v1.0."""

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel


class PolicyRuleEnum(str, Enum):
    R1 = "R1"
    R2 = "R2"
    R3 = "R3"
    R4 = "R4"
    R5 = "R5"
    R6 = "R6"
    R7 = "R7"
    R8 = "R8"
    R9 = "R9"
    R10 = "R10"


class PolicyRule(BaseModel):
    id: PolicyRuleEnum
    title: str
    description: str
    permitted_actions: List[str]
    restricted_actions: List[str] = []

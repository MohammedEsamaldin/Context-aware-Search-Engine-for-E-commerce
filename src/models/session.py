from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Optional

class QueryNode(BaseModel):
    id: str = Field(..., alias="queryId")
    text: str
    timestamp: datetime

class Transition(BaseModel):
    from_query: str = Field(..., alias="from")
    to: str
    count: int
    time_difference: float = Field(..., alias="timeDifference")
    weight: float

class Session(BaseModel):
    id: str = Field(..., alias="sessionId")
    user_id: str = Field(..., alias="userId")
    start_time: datetime = Field(..., alias="startTime")
    end_time: Optional[datetime] = Field(None, alias="endTime")
    queries: List[QueryNode]
    transitions: List[Transition]
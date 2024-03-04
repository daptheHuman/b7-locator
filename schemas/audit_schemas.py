import datetime

from pydantic import BaseModel


class AuditOutput(BaseModel):
    id: int
    url: str
    headers: str
    method: str
    request: str
    timestamp: datetime.datetime

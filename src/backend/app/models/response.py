from enum import Enum
from typing import TypedDict, Optional, Dict


class ResponseType(Enum):
    SUCCESS = "SUCCESS"
    NO_WEB3 = "NO_WEB3"
    NO_INTENT = "NO_INTENT"
    ERROR = "ERROR"


class InsightResponse(TypedDict):
    type: str
    message: str
    metadata: Optional[Dict]
    data: Optional[Dict]
    insight: str

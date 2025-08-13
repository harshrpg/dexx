from dataclasses import dataclass
from typing import List, Optional
from pydantic import BaseModel, ConfigDict

from app.models.prompt_analysis import TechincalResponse, TokenResponse


class TokenDataFetchInput(BaseModel):
    asset_name: Optional[str]
    asset_symbol: Optional[str]


class TokenResearchPlan(BaseModel):
    plan: str
    fallback_plan: str
    asset_name: Optional[str]
    asset_symbol: Optional[str]
    report_type: Optional[str]


@dataclass
class WebAgentResponse(BaseModel):
    model_config = ConfigDict(
        extra="allow",
        validate_assignment=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "report": "Sample report with newlines\nand special characters",
                "reference_links": ["https://example.com"],
            }
        },
    )
    report: str
    reference_links: List[str]


@dataclass
class WorkflowContext:
    query: str
    asset_symbol: Optional[str]
    data: Optional[TechincalResponse]


class DexxResponse(BaseModel):
    query: str
    metadata: Optional[TokenResponse]
    insight: dict
    thread_id: str

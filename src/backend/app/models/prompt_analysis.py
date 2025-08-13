# app/models/prompt_analysis.py
from dataclasses import dataclass
import datetime
from typing import Optional, Dict, List
from pydantic import BaseModel, ConfigDict
from enum import Enum


class PromptType(str, Enum):
    TOKEN_ACTION = "token_action"  # New token analysis request
    CONTEXT_ACTION = "context_action"  # Follow-up to previous token
    GENERAL_QUERY = "general_query"  # General blockchain/crypto questions


class ChartType(str, Enum):
    LINE = "line"
    BAR = "bar"
    PIE = "pie"
    TABLE = "table"
    NONE = "none"


class TimeFrame(BaseModel):
    days: Optional[int]
    from_date: Optional[str]
    to_date: Optional[str]


class ActionParameters(BaseModel):
    chain: Optional[str]
    token_address: Optional[str]
    time_frame: Optional[TimeFrame]
    additional_params: Optional[Dict]


class Action(BaseModel):
    name: str
    parameters: ActionParameters
    chart_type: ChartType


class PromptAnalysis(BaseModel):
    type: PromptType
    token_symbol: Optional[str]
    token_name: Optional[str]
    chain: Optional[str]
    actions: List[Action]
    context_required: bool
    confidence: float
    raw_prompt: str
    contract_address: Optional[str]
    is_followup: bool = (
        False  # Whether this is a follow-up question to a previous token query
    )


@dataclass
class Exchange(BaseModel):
    logo: Optional[str]
    name: Optional[str]
    id: str


@dataclass
class TokenData(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    id: int
    name: str
    symbol: str
    contracts: List[str]
    blockchains: List[str]
    decimals: List[int]
    twitter: Optional[str]
    website: Optional[str]
    logo: Optional[str]
    price: float
    market_cap: float
    liquidity: float
    volume: float
    description: str
    kyc: Optional[str]
    audit: Optional[str]
    total_supply_contracts: List[str]
    total_supply: float
    circulating_supply: int
    circulating_supply_addresses: List[str]
    discord: Optional[str]
    max_supply: Optional[int]
    chat: Optional[str]
    tags: List[str]
    investors: List[Dict]
    distribution: List[Dict]
    release_schedule: List[Dict]
    cexs: List[Exchange]
    listed_at: datetime


@dataclass
class TokenResponse(BaseModel):
    data: TokenData


class ProcessedPrompt(BaseModel):
    prompt_analysis: Optional[PromptAnalysis]
    metadata: Optional[TokenResponse]
    actions: List[Action]


@dataclass
class Sentiment(BaseModel):
    sentiment: dict


class TechincalResponse(BaseModel):
    metadata: TokenResponse
    sentiment: Optional[dict]
    strategy: Optional[dict]

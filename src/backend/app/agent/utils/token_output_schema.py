import json
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from agents import AgentOutputSchemaBase


@dataclass
class TokenMetadata:
    name: str
    symbol: str
    price: float
    market_cap: float
    volume_24h: float
    price_change_24h: float


@dataclass
class SentimentData:
    score: float
    positive_count: int
    negative_count: int
    neutral_count: int
    sources: List[str]


@dataclass
class TokenResponse:
    metadata: TokenMetadata
    sentiment: SentimentData
    technical_indicators: Dict[str, float]
    web_search_required: bool = False


class TokenOutputSchema(AgentOutputSchemaBase):
    """Custom output schema for token responses."""

    def is_plain_text(self) -> bool:
        return False

    def name(self) -> str:
        return "TokenResponse"

    def json_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "metadata": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "symbol": {"type": "string"},
                        "price": {"type": "number"},
                        "market_cap": {"type": "number"},
                        "volume_24h": {"type": "number"},
                        "price_change_24h": {"type": "number"},
                    },
                    "required": [
                        "name",
                        "symbol",
                        "price",
                        "market_cap",
                        "volume_24h",
                        "price_change_24h",
                    ],
                },
                "sentiment": {
                    "type": "object",
                    "properties": {
                        "score": {"type": "number"},
                        "positive_count": {"type": "integer"},
                        "negative_count": {"type": "integer"},
                        "neutral_count": {"type": "integer"},
                        "sources": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": [
                        "score",
                        "positive_count",
                        "negative_count",
                        "neutral_count",
                        "sources",
                    ],
                },
                "technical_indicators": {
                    "type": "object",
                    "properties": {
                        "MACD": {"type": "number"},
                        "RSI": {"type": "number"},
                        "EMA": {"type": "number"},
                        "SMA": {"type": "number"},
                        "Bollinger_Upper": {"type": "number"},
                        "Bollinger_Lower": {"type": "number"},
                    },
                    "required": ["MACD", "RSI"],
                },
                "web_search_required": {"type": "boolean"},
            },
            "required": [
                "metadata",
                "sentiment",
                "technical_indicators",
                "web_search_required",
            ],
        }

    def is_strict_json_schema(self) -> bool:
        return False

    def validate_json(self, json_str: str) -> TokenResponse:
        json_obj = json.loads(json_str)

        # Validate and create TokenMetadata
        metadata = TokenMetadata(
            name=json_obj["metadata"]["name"],
            symbol=json_obj["metadata"]["symbol"],
            price=json_obj["metadata"]["price"],
            market_cap=json_obj["metadata"]["market_cap"],
            volume_24h=json_obj["metadata"]["volume_24h"],
            price_change_24h=json_obj["metadata"]["price_change_24h"],
        )

        # Validate and create SentimentData
        sentiment = SentimentData(
            score=json_obj["sentiment"]["score"],
            positive_count=json_obj["sentiment"]["positive_count"],
            negative_count=json_obj["sentiment"]["negative_count"],
            neutral_count=json_obj["sentiment"]["neutral_count"],
            sources=json_obj["sentiment"]["sources"],
        )

        # Create TokenResponse
        return TokenResponse(
            metadata=metadata,
            sentiment=sentiment,
            technical_indicators=json_obj["technical_indicators"],
            web_search_required=json_obj.get("web_search_required", False),
        )

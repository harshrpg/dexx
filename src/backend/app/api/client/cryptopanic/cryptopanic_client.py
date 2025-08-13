import os
import requests
from typing import Dict, Optional, List
import logging
from dotenv import load_dotenv

from app.models.prompt_analysis import Sentiment

load_dotenv()


class CryptoPanicClient:
    """Client for interacting with CryptoPanic API"""

    BASE_URL = "https://cryptopanic.com/api/v1"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("CRYPTOPANIC_API_KEY")
        if not self.api_key:
            raise ValueError("CryptoPanic API key is required")
        self.logger = logging.getLogger(__name__)

    def get_news_for_symbol(
        self,
        symbol: str,
        kind: str = "news",
        filter_type: Optional[str] = None,
        public: bool = True,
        metadata: bool = False,
    ) -> Sentiment:
        """
        Fetch news for a specific cryptocurrency symbol.

        Args:
            symbol: Cryptocurrency symbol (e.g., BTC, ETH)
            kind: Type of content (news or media)
            filter_type: Optional filter (rising, hot, bullish, bearish, important)
            public: Whether to use public API
            metadata: Whether to include extra metadata (PRO users only)

        Returns:
            Dictionary containing news data and sentiment analysis
        """
        try:
            params = {
                "auth_token": self.api_key,
                "currencies": symbol,
                "kind": kind,
                "public": "true" if public else "false",
            }

            if filter_type:
                params["filter"] = filter_type

            response = requests.get(f"{self.BASE_URL}/posts/", params=params)
            response.raise_for_status()

            data = response.json()

            # Calculate sentiment based on news
            sentiment_analysis = self._analyze_sentiment(data.get("results", []))
            self.logger.info(f"Sentiment analysis: {sentiment_analysis}")

            # return {
            #     "news": data.get("results", []),
            #     "sentiment": sentiment_analysis
            # }
            return Sentiment(sentiment=sentiment_analysis)

        except Exception as e:
            self.logger.error(
                f"Error fetching news for {symbol}: {str(e)}", exc_info=True
            )
            raise

    def _analyze_sentiment(self, news_items: List[Dict]) -> Dict:
        """
        Analyze sentiment from news items.

        Args:
            news_items: List of news items from CryptoPanic API

        Returns:
            Dictionary containing sentiment analysis
        """
        if not news_items:
            return {
                "overall": "neutral",
                "score": 0,
                "bullish_count": 0,
                "bearish_count": 0,
                "neutral_count": 0,
            }

        sentiment_counts = {"bullish": 0, "bearish": 0, "neutral": 0}

        for item in news_items:
            votes = item.get("votes", {})
            # Count sentiment based on votes
            if votes.get("positive", 0) > votes.get("negative", 0):
                sentiment_counts["bullish"] += 1
            elif votes.get("negative", 0) > votes.get("positive", 0):
                sentiment_counts["bearish"] += 1
            else:
                sentiment_counts["neutral"] += 1

        total_items = len(news_items)
        sentiment_score = (
            (sentiment_counts["bullish"] - sentiment_counts["bearish"]) / total_items
            if total_items > 0
            else 0
        )

        # Determine overall sentiment
        if sentiment_score > 0.2:
            overall = "bullish"
        elif sentiment_score < -0.2:
            overall = "bearish"
        else:
            overall = "neutral"

        return {
            "overall": overall,
            "score": sentiment_score,
            "bullish_count": sentiment_counts["bullish"],
            "bearish_count": sentiment_counts["bearish"],
            "neutral_count": sentiment_counts["neutral"],
        }

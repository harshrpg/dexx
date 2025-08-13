from typing import Dict, Optional
from app.models.prompt_analysis import Sentiment, TokenResponse
from app.services.data_access.data_access_service import DataAccessService


class Tools:
    def __init__(self) -> None:
        self.das = DataAccessService()

    def fetch_token_metadata(
        self, token_name: str = None, token_symbol: str = None
    ) -> Optional[TokenResponse]:
        if (token_name == None or token_name.strip() == "") and (
            token_symbol == None or token_symbol.strip() == ""
        ):
            return None
        if token_symbol:
            return self.das.fetch_metadata(token_symbol=token_symbol)
        else:
            return self.das.fetch_metadata(token_query=token_name)

    def fetch_sentiment_for_token(
        self, token_name_or_symbol: str
    ) -> Optional[Sentiment]:
        return self.das.fetch_sentiment_for_token(token_symbol=token_name_or_symbol)

    def fetch_strategy_for_token(
        self, token_symbol: str, blockchain: str
    ) -> Optional[Dict]:
        return self.das.fetch_ohlcv_data(
            token_symbol=token_symbol, blockchain=blockchain
        )

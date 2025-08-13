from typing import Dict, Optional
import requests
from app.core.config import settings
from app.models.api.routes import MobulaEndpoints


class MetacoreClient:

    def __init__(self):
        self.url = f"{settings.MOBULA_PRODUCTION_API_ENDPOINT}/{MobulaEndpoints.REST_API}/{MobulaEndpoints.REST_API_VERSION}"

    def get_all_cryptocurrencies(self):
        url = f"{self.url}/{MobulaEndpoints.GET_ALL_CRYPTOCURRENCIES}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    def get_metadata(self, query_string: Dict):
        url = f"{self.url}/{MobulaEndpoints.METADATA}"
        response = requests.get(url=url, params=query_string)
        response.raise_for_status()
        return response.json()

    def get_ohlcv_data(
        self,
        asset: str,
        resolution: str = "1d",
        from_time: Optional[int] = None,
        to_time: Optional[int] = None,
        amount: Optional[int] = None,
        blockchain: Optional[str] = None,
    ) -> Dict:
        """Fetch OHLCV (Open, High, Low, Close, Volume) data from Mobula API.
        
        Args:
            asset: Token contract address or symbol
            resolution: Time resolution (1min, 5min, 15min, 1h, 2h, 4h, 1d, 7d, 30d)
            from_time: Start timestamp (optional)
            to_time: End timestamp (optional)
            amount: Number of candles to fetch (optional)
            blockchain: Blockchain network (optional)
            
        Returns:
            Dict containing OHLCV data
        """
        url = f"{self.url}/{MobulaEndpoints.MARKET_HISTORY}"
        params = {
            "symbol": asset,
            "blockchain": blockchain
        }
        
        # if from_time:
        #     params["from"] = from_time
        # if to_time:
        #     params["to"] = to_time
        # if amount:
        #     params["amount"] = amount
        # if blockchain:
        #     params["blockchain"] = blockchain
            
        response = requests.get(url=url, params=params)
        response.raise_for_status()
        return response.json()

    def get_latest_tokens(self):
        url = f"{self.url}/{MobulaEndpoints.LATEST_TOKENS}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
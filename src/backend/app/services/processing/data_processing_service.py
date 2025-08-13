import logging
from concurrent import futures
from app.models.prompt_analysis import TokenResponse
from app.services.data_access.data_access_service import DataAccessService
from app.services.technical_analysis.technical_analysis_service import TechnicalAnalysisService

class DataProcessingService:
    def __init__(self):
        self.data_access_service = DataAccessService()
        self.technical_analysis_service = TechnicalAnalysisService()
        self.logger = logging.getLogger(__name__)

    def fetch_token_data_and_process(self, token_symbol: str):
        metadata = self.data_access_service.fetch_metadata(token_symbol=token_symbol)
        blockchain = self.identify_blockchain(metadata)
        
        with futures.ThreadPoolExecutor() as executor:
            ohlcv_future = executor.submit(
                self.data_access_service.fetch_ohlcv_data,
                token_symbol=token_symbol,
                blockchain=blockchain
            )
            sentiment_future = executor.submit(
                self.data_access_service.fetch_sentiment_for_token,
                token_symbol=token_symbol
            )
            
            # Get results
            ohlcv_data = ohlcv_future.result()
            sentiments = sentiment_future.result()
        
        # Calculate indicators from OHLCV data
        # indicators = self.technical_analysis_service.calculate_indicators(ohlcv_data)

        return {
            "metadata": metadata.model_dump() if metadata else None,
            "indicators": ohlcv_data["indicators"],
            "sentiments": sentiments
        }
    
    @property
    def blockchain_priority(self) -> list:
        """Priority order for blockchains from highest to lowest."""
        return [
            'Ethereum',
            'Solana',
            'Binance Smart Chain', 
            'BSC',
            'Polygon',
            'SUI',
            'Optimism'
        ]

    def identify_blockchain(self, metadata: TokenResponse):
        """
        Identify the blockchain for a token based on priority order.
        Returns the highest priority blockchain found in metadata, or first available if none match.
        """
        if not metadata.data.blockchains:
            return None
            
        # Check for each blockchain in priority order
        for priority_chain in self.blockchain_priority:
            if priority_chain in metadata.data.blockchains:
                return priority_chain
                
        # If no priority chains found, return first available
        return metadata.data.blockchains[0]
    
    def fetch_latest_tokens(self):
        return self.data_access_service.fetch_latest_tokens()
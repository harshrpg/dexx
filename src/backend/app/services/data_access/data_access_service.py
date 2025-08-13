from typing import Optional, Dict, List
import logging
from app.api.client.cryptopanic.cryptopanic_client import CryptoPanicClient
from app.api.client.mobula.metacore_client import MetacoreClient
from app.models.prompt_analysis import Sentiment, TokenResponse
from app.services.technical_analysis.technical_analysis_service import (
    TechnicalAnalysisService,
)
import time
from fastapi import HTTPException
from typing import Optional
from app.models.response import ResponseType


class DataAccessService:
    """Service for accessing token metadata from Mobula API.

    This service handles fetching and processing token metadata, with support for
    querying by contract address, token symbol, or general token query.
    """

    # Chain priority map (lower number = higher priority)
    CHAIN_PRIORITY = {
        "ethereum": 0,
        "polygon": 1,
        "bnb smart chain (bep20)": 2,
        "arbitrum": 3,
        "optimistic": 4,
        "avalanche c-chain": 5,
        "base": 6,
        "solana": 7,
    }

    def __init__(self):
        """Initialize the service with Mobula client."""
        self.mobula_client = MetacoreClient()
        self.technical_analysis = TechnicalAnalysisService()
        self.crypto_panic_client = CryptoPanicClient()
        self.logger = logging.getLogger(__name__)

    def fetch_sentiment_for_token(self, token_symbol: str) -> Sentiment:
        return self.crypto_panic_client.get_news_for_symbol(symbol=token_symbol)

    def fetch_latest_tokens(self) -> Optional[Dict]:
        """Fetch latest tokens from Mobula API.

        Returns:
            Dictionary containing latest token data if successful, None otherwise
        """
        self.logger.info("Fetching latest tokens")

        try:
            self.logger.debug("Making API call to Mobula")
            latest_tokens = self.mobula_client.get_latest_tokens()
            self.logger.debug(f"Latest tokens response: {latest_tokens}")

            if latest_tokens is None:
                self.logger.warning("Received empty response from API")
                return None

            return latest_tokens

        except Exception as e:
            self.logger.error(f"Error fetching latest tokens: {e}")
            return None

    def fetch_metadata(
        self,
        token_query: Optional[str] = None,
        contract_address: Optional[str] = None,
        chain: Optional[str] = None,
        token_symbol: Optional[str] = None,
    ) -> Optional[TokenResponse]:
        """Fetch token metadata from Mobula API.

        Args:
            token_query: General search query for token
            contract_address: Specific contract address to search for
            chain: Blockchain network to filter by
            token_symbol: Token symbol to search for

        Returns:
            TokenResponse object containing metadata if found, None otherwise

        Raises:
            ValueError: If metadata format is invalid or no search criteria provided
        """
        self.logger.info(
            f"Fetching metadata with params: token_query={token_query}, contract={contract_address}, chain={chain}, symbol={token_symbol}"
        )

        query_string = self._build_query_string(
            token_query, contract_address, chain, token_symbol
        )
        self.logger.debug(f"Built query string: {query_string}")

        if not query_string:
            self.logger.error("No search criteria provided")
            raise ValueError("At least one search criteria must be provided")

        try:
            self.logger.debug("Making API call to Mobula")
            raw_metadata = self.mobula_client.get_metadata(query_string)
            self.logger.debug(f"Raw metadata: {raw_metadata}")

            # Handle empty responses
            if raw_metadata is None:
                self.logger.warning("Received empty response from API")
                return None

            # Validate response structure
            if not isinstance(raw_metadata, dict) or "data" not in raw_metadata:
                self.logger.error(f"Invalid response format: {raw_metadata}")
                raise ValueError("Invalid response format: missing required fields")

            # Handle empty data
            if raw_metadata["data"] is None:
                self.logger.warning("Response data is None")
                return None

            self.logger.debug("Validating response with TokenResponse model")
            metadata = TokenResponse.model_validate(raw_metadata)

            if metadata.data:
                # Validate that the returned token matches what we requested
                requested_symbol = token_symbol or token_query
                if (
                    requested_symbol
                    and metadata.data.symbol.upper() != requested_symbol.upper()
                ):
                    self.logger.warning(
                        f"Token symbol mismatch. Requested: {requested_symbol}, Got: {metadata.data.symbol}"
                    )
                    return None

                self.logger.debug(f"Filtering metadata for chain: {chain}")
                self._filter_metadata(metadata, chain)
                self.logger.info(
                    f"Successfully fetched metadata for {metadata.data.symbol}"
                )
                return metadata

            self.logger.warning("No valid data found in response")
            return None

        except Exception as e:
            self.logger.error(f"Error fetching metadata: {str(e)}", exc_info=True)
            raise ValueError(f"Failed to fetch or process metadata: {str(e)}")

    def fetch_ohlcv_data(
        self, token_symbol: str, resolution: str = "1d", blockchain: str = None
    ) -> Optional[Dict]:
        """Fetch OHLCV data and calculate technical indicators.

        Args:
            token_symbol: Token symbol to search for
            resolution: Time resolution (1min, 5min, 15min, 1h, 2h, 4h, 1d, 7d, 30d)

        Returns:
            Dictionary containing OHLCV data and technical indicators if found, None otherwise
        """
        try:
            # Calculate time range for 7 days
            end_time = int(time.time())
            start_time = end_time - (7 * 24 * 60 * 60)

            # Fetch OHLCV data
            self.logger.info(f"Fetching OHLCV data for {token_symbol}")
            ohlcv_data = self.mobula_client.get_ohlcv_data(
                asset=token_symbol,
                resolution=resolution,
                from_time=start_time,
                to_time=end_time,
                blockchain=blockchain,
            )

            if not ohlcv_data or "data" not in ohlcv_data:
                self.logger.warning("No OHLCV data found")
                return None

            # Calculate technical indicators
            self.logger.info("Calculating technical indicators")
            indicators = self.technical_analysis.calculate_indicators(
                ohlcv_data["data"]
            )
            self.logger.debug(f"OHLCV Indicators: {indicators}")
            return {"ohlcv": ohlcv_data["data"], "indicators": indicators}

        except Exception as e:
            self.logger.error(f"Error fetching OHLCV data: {str(e)}", exc_info=True)
            return None

    def _build_query_string(
        self,
        token_query: Optional[str],
        contract_address: Optional[str],
        chain: Optional[str],
        token_symbol: Optional[str],
    ) -> Dict[str, str]:
        """Build the query string for the Mobula API request.

        Prioritizes contract address > token symbol > general query.
        """
        query_string = {}

        if contract_address:
            self.logger.debug(f"Using contract address for query: {contract_address}")
            query_string["asset"] = contract_address
        elif token_symbol:
            self.logger.debug(f"Using token symbol for query: {token_symbol}")
            query_string["symbol"] = token_symbol
        elif token_query:
            self.logger.debug(f"Using general token query: {token_query}")
            query_string["asset"] = token_query

        # WARN: Chain query is not working as expected
        # if chain:
        #     query_string["blockchain"] = chain

        return query_string

    def _get_chain_priority(self, chain: str) -> Optional[int]:
        """Get the priority value for a given chain.

        Lower numbers indicate higher priority.
        Returns None if chain is not in priority list.
        """
        priority = self.CHAIN_PRIORITY.get(chain.lower())
        self.logger.debug(f"Chain priority for {chain}: {priority}")
        return priority

    def _filter_metadata(self, metadata: TokenResponse, chain: Optional[str]) -> None:
        """Filter metadata based on chain and keep only relevant data.

        If chain is specified and found, keeps that chain's data.
        If chain is not found or not specified:
        - First tries to find the highest priority chain from available chains
        - If no priority chains found, uses the last chain in the list
        """
        if not metadata.data or not metadata.data.contracts:
            self.logger.warning("No contracts found in metadata")
            return

        if chain and metadata.data.blockchains:
            self.logger.debug(f"Filtering for specified chain: {chain}")
            # Filter by specified chain
            filtered_indices = [
                i
                for i, blockchain in enumerate(metadata.data.blockchains)
                if blockchain.lower() == chain.lower()
            ]

            if filtered_indices:
                # Use the specified chain
                selected_index = filtered_indices[0]
                self.logger.debug(f"Found matching chain at index {selected_index}")
            else:
                # Fall back to best available chain
                self.logger.debug(
                    "Specified chain not found, falling back to best available chain"
                )
                selected_index = self._get_best_available_chain_index(
                    metadata.data.blockchains
                )
        else:
            # No chain specified, find best available chain
            self.logger.debug("No chain specified, finding best available chain")
            selected_index = self._get_best_available_chain_index(
                metadata.data.blockchains
            )

        # Update metadata with selected chain's data
        self.logger.debug(f"Updating metadata with chain at index {selected_index}")
        metadata.data.contracts = [metadata.data.contracts[selected_index]]
        metadata.data.blockchains = [metadata.data.blockchains[selected_index]]
        metadata.data.decimals = [metadata.data.decimals[selected_index]]
        self.logger.info(f"Updated metadata")

    def _get_best_available_chain_index(self, chains: List[str]) -> int:
        """Get the index of the best available chain from a list of chains.

        First tries to find the highest priority chain from the priority list.
        If no priority chains are found, returns the last chain in the list.
        """
        if not chains:
            self.logger.warning("No chains available")
            return 0

        # Get priorities for all chains that are in our priority list
        chain_priorities = [
            (priority, i)
            for i, chain in enumerate(chains)
            if (priority := self._get_chain_priority(chain)) is not None
        ]

        # If we found any priority chains, use the highest priority one
        if chain_priorities:
            best_chain_index = min(chain_priorities, key=lambda x: x[0])[1]
            self.logger.debug(
                f"Selected highest priority chain at index {best_chain_index}"
            )
            return best_chain_index

        # If no priority chains found, use the last chain in the list
        self.logger.debug("No priority chains found, using last chain in list")
        return len(chains) - 1

    async def get_selected_token_metadata(
        self, symbol: str, chain: Optional[str] = None
    ):
        try:
            metadata = self.fetch_metadata(token_symbol=symbol, chain=chain)
            if not metadata:
                raise HTTPException(
                    status_code=404, detail=f"No metadata found for {symbol}"
                )

            return {
                "type": ResponseType.SUCCESS,
                "message": f"Metadata and chart rebuilt for {symbol}",
                "metadata": metadata.model_dump(),
                "symbol": symbol,
            }

        except Exception as e:
            logging.error(
                f"[DataAccessService] Failed to fetch metadata for {symbol}: {e}",
                exc_info=True,
            )
            raise HTTPException(status_code=500, detail=str(e))

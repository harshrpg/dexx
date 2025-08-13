import logging
import os
from typing import Dict, List
from app.models.response import ResponseType
from app.api.client.moralis.token_api_client import TokenApiClient
from app.core.nlp.analyzer.llm_prompt_analyzer import (
    LLMPromptAnalyzer,
    PromptAnalysisResult,
)
from app.core.nlp.parser.chain_extractor import ChainExtractor
from app.core.nlp.parser.endpoint_identifier import EndpointIdentifier
from app.core.nlp.parser.keyword_mappings import KeywordMappings
from app.core.nlp.parser.nlp_processor import NLPProcessor
from app.core.nlp.parser.prompt_parser import PromptParser
from app.core.nlp.parser.time_extractor import TimeExtractor
from app.core.nlp.parser.token_resolver import TokenResolver
from app.services.endpoint_params_manager import EndpointParamsManager
from app.services.data_access.data_access_service import DataAccessService

data_service = DataAccessService()

class PromptParsingService:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize_parser()
        return cls._instance

    def _initialize_parser(self):
        # Initialize existing components
        self.mappings = KeywordMappings()
        self._prompt_parser = PromptParser()
        self.nlp_processor = NLPProcessor()
        self.time_extractor = TimeExtractor()
        self.chain_extractor = ChainExtractor(self.mappings.chain_mappings)
        self.endpoint_identifier = EndpointIdentifier(self.mappings.action_mappings)
        self.token_resolver = TokenResolver(self.mappings.token_symbols)
        self.token_client = TokenApiClient(api_key=os.getenv("MORALIS_API_KEY"))
        self.endpoint_params_manager = EndpointParamsManager()

        # Initialize LLM analyzer
        self.llm_analyzer = LLMPromptAnalyzer()

        # Logging initialization
        for component in [
            "KeywordMappings",
            "PromptParser",
            "NLPProcessor",
            "TimeExtractor",
            "ChainExtractor",
            "EndpointIdentifier",
            "TokenResolver",
            "TokenApiClient",
            "EndpointParamsManager",
            "LLMPromptAnalyzer",
        ]:
            logging.debug(f"{component} initialized")

    async def parse_prompt(self, prompt: str, use_llm: bool) -> Dict:
        """
        Parse the prompt using either LLM or traditional approach.
        Args:
            prompt: The user's prompt
            use_llm: Whether to try LLM first (falls back to traditional if LLM fails)
        """
        try:
            if use_llm:
                try:
                    return await self._parse_with_llm(prompt)
                except Exception as e:
                    logging.warning(
                        f"LLM parsing failed, falling back to traditional: {str(e)}"
                    )
                    return await self._parse_traditional(prompt)
            else:
                return await self._parse_traditional(prompt)

        except Exception as e:
            logging.error(f"Error in parse_prompt: {str(e)}")
            raise

    async def _parse_with_llm(self, prompt: str) -> Dict:
        """Parse prompt using LLM approach"""
        # Get LLM analysis
        analysis = await self.llm_analyzer.analyze_prompt(prompt)

        # If confidence is too low, fall back to traditional
        if analysis.confidence < 0.7:
            return await self._parse_traditional(prompt)

        # Get token metadata if token was identified
        token_info = (
            await self._process_token_info(
                prompt, chain=analysis.chain or "eth", llm_analysis=analysis
            )
            if analysis.token_symbol
            else {"is_web3": True, "metadata": None, "address": None}
        )

        # Build API calls based on LLM analysis
        api_calls = {}
        if analysis.action:
            api_calls[analysis.action] = {
                "params": self._prepare_api_params(
                    chain=analysis.chain or "eth",
                    token_info=token_info,
                    endpoint={"endpoint": analysis.action},
                    time_params=analysis.parameters.get("time_params", {}),
                    nlp_info={"temporal_info": []},  # Could be enhanced with LLM output
                ),
                "confidence": analysis.confidence,
            }

        return {
            "metadata": token_info["metadata"],
            "api_calls": api_calls,
            "is_web3_query": True,
            "original_prompt": prompt,
            "llm_analysis": {
                "token": analysis.token_symbol,
                "chain": analysis.chain,
                "intent": analysis.intent,
                "confidence": analysis.confidence,
            },
        }

    async def _parse_traditional(self, prompt: str) -> Dict:
        """Original parsing logic"""
        doc = self.nlp_processor.nlp(prompt.lower())
        chain = self.chain_extractor.extract_chain(prompt, doc)

        token_info = await self._process_token_info(prompt, chain=chain)

        if not token_info["is_web3"]:
            return {
                "metadata": None,
                "api_calls": None,
                "is_web3_query": False,
                "original_prompt": prompt,
            }

        return await self._build_web3_response(prompt, chain, token_info)

    async def parse(self, prompt: str, use_llm: bool = True) -> Dict:
        """Main entry point for prompt parsing"""
        if not self._prompt_parser:
            raise RuntimeError("PromptParser has not been initialized.")
        return await self.parse_prompt(prompt, use_llm=use_llm)

    def execute(self, action: Dict) -> Dict:
        """Perform the next prescribed action"""
        if not self._prompt_parser:
            raise RuntimeError("PromptParser has not been initialized.")
        token_client = TokenApiClient(api_key=os.getenv("MORALIS_API_KEY"))
        return self._prompt_parser.execute_api_calls(token_client, action)

    async def _process_token_info(
        self, prompt: str, chain: str, llm_analysis: PromptAnalysisResult = None
    ) -> Dict:
        metadata, address = await self.token_resolver.resolve_token_metadata(
            self.token_client, prompt, chain
        )
        return {
            "is_web3": bool(metadata),
            "metadata": metadata,
            "address": address,
        }

    async def _build_web3_response(
        self, prompt: str, chain: str, token_info: Dict
    ) -> Dict:
        time_params = self.time_extractor.extract_parameters(prompt)
        endpoints = self._identify_relevant_endpoints(prompt)
        nlp_info = self.nlp_processor.process_text(prompt)
        api_calls = {}
        for endpoint in endpoints:
            api_calls[endpoint["endpoint"]] = {
                "params": self._prepare_api_params(
                    chain, token_info, endpoint, time_params, nlp_info
                ),
                "confidence": endpoint["confidence"],
            }

        return {
            "metadata": token_info["metadata"],
            "api_calls": api_calls,
            "is_web3_query": True,
            "original_prompt": prompt,
        }

    def _identify_relevant_endpoints(self, prompt: str) -> List[Dict]:
        """Identify which API endpoints are relevant for the prompt"""
        doc = self.nlp_processor.nlp(prompt.lower())
        return self.endpoint_identifier.identify_endpoints(prompt, doc)

    def _prepare_api_params(
        self,
        chain: str,
        token_info: Dict,
        endpoint: Dict,
        time_params: Dict,
        nlp_info: Dict,
    ) -> Dict:
        """Prepare API parameters for specific endpoints."""
        base_params = {"chain": chain}
        # if token_info.get("address"):
        #     base_params["address"] = token_info["address"]

        # Define endpoint-specific parameters
        # endpoint_params = {
        #     "get_token_owners": {"limit": 100, "order": "DESC"},
        #     "get_token_metadata": {"include_supply": True, "include_platform": True},
        #     "get_token_price": {"include_24hr_change": True, "include_platform": True},
        #     "get_top_profitable_wallet_per_token": {
        #         "days": self._extract_timeframe(nlp_info) if nlp_info else "all"
        #     },
        #     "get_token_transfers": {"order": "DESC"},
        # }

        # # Add contract address based on endpoint
        # if endpoint == "get_token_owners" and contract_address:
        #     base_params["token_address"] = contract_address
        # elif endpoint != "get_token_owners" and contract_address:
        #     base_params["address"] = contract_address

        # # Add time parameters for all endpoints except get_top_profitable_wallet_per_token
        # if endpoint != "get_top_profitable_wallet_per_token" and time_params:
        #     base_params.update(time_params)

        # # Add endpoint-specific parameters
        # if endpoint in endpoint_params:
        #     base_params.update(endpoint_params[endpoint])

        # if time_params:
        #     base_params.update(time_params)

        # return {**base_params, **endpoint.get("default_params", {})}

        # return base_params
        return self.endpoint_params_manager.get_params(
            endpoint["endpoint"],
            base_params,
            token_info.get("address"),
            time_params,
            nlp_info=nlp_info,
        )
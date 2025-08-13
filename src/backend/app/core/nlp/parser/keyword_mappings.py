from functools import lru_cache
import json
import logging
from pathlib import Path
from typing import Dict, Set

from app.api.client.mobula.metacore_client import MetacoreClient
from app.models.chains import ChainMapping
from app.models.token_symbols import GetAllCryptocurrencies_Mobula_Data


@lru_cache
class KeywordMappings:

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self._chain_mappings = None
        self._token_symbols_mappings = None
        self._action_mappings = None
        self.mobula_client = MetacoreClient()

    @property
    def chain_mappings(self) -> ChainMapping:
        if self._chain_mappings is None:
            self._chain_mappings = self._load_chain_mapping()
        return self._chain_mappings

    @property
    def token_symbols(self) -> Dict[str, Set[str]]:
        if self._token_symbols_mappings is None:
            self._token_symbols_mappings = self._load_token_symbols()
        return self._token_symbols_mappings

    @property
    def action_mappings(self) -> Dict[str, Dict[str, Set[str]]]:
        if self._action_mappings is None:
            self._action_mappings = self._load_action_mappings()
        return self._action_mappings

    def _load_chain_mapping(self) -> ChainMapping:
        try:
            config_path = (
                Path(__file__).parent.parent.parent.parent
                / "config"
                / "blockchain_networks.json"
            )
            with open(config_path, "r") as f:
                chain_data = json.load(f)
                validated_data = ChainMapping.model_validate(chain_data)
                return validated_data
        except FileNotFoundError:
            logging.error("Config file not found")
            raise

    def _load_action_mappings(self):
        return {
            "get_token_owners": {
                "primary": ["owners", "holding", "holders", "owning", "hold"],
                "context": ["wallet", "address", "who", "accounts"],
                "quantity": ["many", "count", "number", "total"],
                "description": "Get list of addresses that own a specific token",
                "required_params": ["token_address", "chain"],
            },
            "get_token_metadata": {
                "primary": [
                    "information",
                    "info",
                    "metadata",
                    "details",
                    "about",
                    "market cap",
                    "mkt",
                    "cap",
                    "capitalization",
                    "capitalisation",
                    "token",
                    "token info",
                    "market",
                    "change",
                    "price",
                    "latest",
                    "volume",
                    "fully",
                    "diluted",
                    "valuation",
                    "logo",
                    "socials",
                ],
                "context": ["contract", "symbol", "name", "decimals", "supply"],
                "attributes": ["standard", "type", "platform"],
                "description": "Get token information (name, symbol, decimals, contract address, etc)",
                "required_params": ["token_address", "chain"],
            },
            "get_token_price": {
                "primary": ["price", "cost", "worth", "value"],
                "temporal": ["current", "now", "latest", "today"],
                "attributes": ["change", "volume", "market", "cap"],
                "description": "Get current price of a token",
                "required_params": ["token_address", "chain"],
            },
            "get_top_profitable_wallet_per_token": {
                "primary": [
                    "performing",
                    "profitable",
                    "profit",
                    "performance",
                    "top",
                ],
                "context": ["traders", "investors", "wallets", "addresses"],
                "attributes": ["best", "highest", "most", "successful"],
                "description": "Get the most profitable wallets for a specific token",
                "required_params": ["token_address", "chain"],
            },
            "get_wallet_active_chains": {
                "primary": ["chains", "active", "networks"],
                "context": ["blockchain", "protocol", "platform"],
                "attributes": ["used", "activity", "interaction"],
                "description": "Get list of blockchain networks where a wallet is active",
                "required_params": ["wallet_address"],
            },
            "get_token_stats": {
                "primary": [
                    "stats",
                    "statistics",
                    "analytics",
                    "numbers",
                    "metrics",
                ],
                "temporal": ["daily", "weekly", "monthly", "yearly"],
                "attributes": ["volume", "liquidity", "holders", "transactions"],
                "description": "Get token statistics including volume, liquidity, holders count",
                "required_params": ["token_address", "chain"],
            },
            "get_token_transfers": {
                "primary": [
                    "transfers",
                    "transactions",
                    "movement",
                    "sent",
                    "received",
                ],
                "temporal": ["recent", "latest", "past", "history"],
                "attributes": ["in", "out", "between", "from", "to"],
                "description": "Get transfer history of a token",
                "required_params": ["token_address", "chain"],
            },
        }

    def _load_token_symbols(self):
        try:
            response = self.mobula_client.get_all_cryptocurrencies()
            validated_data = GetAllCryptocurrencies_Mobula_Data.model_validate(response)
            token_symbols: Dict[str, Set[str]] = {}

            # Process each cryptocurrency
            for crypto in validated_data.data:
                symbol = crypto.symbol.upper()
                name = crypto.name.lower()

                # Create base variations of the token name
                variations = {
                    name,  # Original name in lowercase
                    name.replace(" ", ""),  # Name without spaces
                    symbol.lower(),  # Symbol in lowercase
                    f"{name} token",  # Common variation with 'token'
                    f"{symbol.lower()} token",  # Symbol with 'token'
                }

                # Add additional variations while keeping original terms
                if "coin" in name.lower():
                    variations.add(name)  # Keep original with "coin"
                    variations.add(f"{name} coin")  # Add explicit coin suffix

                if "protocol" in name.lower():
                    variations.add(name)  # Keep original with "protocol"
                    variations.add(f"{name} protocol")  # Add explicit protocol suffix

                if "finance" in name.lower():
                    variations.add(name)  # Keep original with "finance"
                    variations.add(f"{name} finance")  # Add explicit finance suffix

                # Add chain-specific variations if applicable
                if any(
                    chain in name.lower()
                    for chain in ["ethereum", "bitcoin", "binance"]
                ):
                    variations.add(f"{name} chain")
                    variations.add(f"{name} network")

                # Remove empty strings and normalize whitespace
                variations = {v.strip() for v in variations if v.strip()}

                # Add to token symbols dictionary
                token_symbols[symbol] = variations
            return token_symbols
        except Exception as e:
            logging.error(f"Error loading token symbols from Mobula API: {str(e)}")
            return {  # Base Ecosystem Tokens
                "BALD": {"bald", "baldcoin", "based and bald"},
                "TOSHI": {"toshi", "toshitoken"},
                "BASED": {"based", "based token", "based finance"},
                "MEM": {"mem", "meme token", "meme coin"},
                "PENDLE": {"pendle", "pendle token"},
                "DOSU": {"dosu", "dosu token"},
                "ABASE": {"abase", "abase token"},
                "FXN": {"fxn", "function token", "function x"},
                "ECHELON": {"echelon", "echelon prime"},
                # Solana Ecosystem Tokens
                "SOL": {"solana", "sol"},
                "BONK": {"bonk", "bonk token", "bonk coin"},
                "RAY": {"raydium", "ray token"},
                "SRM": {"serum", "srm token"},
                "SAMO": {"samoyedcoin", "samo"},
                "ORCA": {"orca", "orca token"},
                "STEP": {"step finance", "step"},
                "ATLAS": {"star atlas", "atlas token"},
                "COPE": {"cope", "cope token"},
                # AI Tokens
                "AGIX": {"singularitynet", "agix token"},
                "OCEAN": {"ocean protocol", "ocean token"},
                "FET": {"fetch.ai", "fetch token", "fet token"},
                "GRT": {"graph", "graph token"},
                "NMR": {"numeraire", "nmr token"},
                "RLC": {"iexec", "rlc token"},
                "INJ": {"injective", "injective protocol"},
                "aixbt": {"aixbt", "virtuals", "AIXBT"},
                "ai16z": {"eliza", "elizaos"},
                # Major Stablecoins
                "USDT": {"tether", "usdt", "tether token"},
                "USDC": {"usd coin", "usdc", "circle"},
                "DAI": {"dai", "dai stablecoin"},
                # Popular DeFi Tokens
                "LINK": {"chainlink", "link token", "link"},
                "UNI": {"uniswap", "uni token"},
                "AAVE": {"aave", "aave token"},
                "SNX": {"synthetix", "snx token"},
                "CRV": {"curve", "curve dao", "curve token"},
                # Meme Coins
                "DOGE": {"dogecoin", "doge"},
                "SHIB": {"shiba inu", "shib", "shiba"},
                "PEPE": {"pepe", "pepe coin"},
                "FLOKI": {"floki", "floki inu"},
                "WOJAK": {"wojak", "wojak coin"},
                "SNEK": {"snek", "snek coin"},
                # Major Layer 1 Tokens
                "ETH": {"ethereum", "ether", "eth"},
                "BTC": {"bitcoin", "btc"},
                "BNB": {"binance coin", "bnb", "binance token"},
                "MATIC": {"polygon", "matic token", "matic"},
                "AVAX": {"avalanche", "avax"},
                "ARB": {"arbitrum", "arb", "arbitrum token"},
                "OP": {"optimism", "op token"},
                # GameFi Tokens
                "AXS": {"axie infinity", "axs token"},
                "SAND": {"sandbox", "sand token"},
                "MANA": {"decentraland", "mana token"},
                "ILV": {"illuvium", "ilv token"},
                # Privacy Tokens
                "XMR": {"monero", "xmr"},
                "ZEC": {"zcash", "zec"},
                "SCRT": {"secret", "secret network", "scrt token"},
            }

    # def _load_token_symbols(self):
    # return {  # Base Ecosystem Tokens
    #     "BALD": {"bald", "baldcoin", "based and bald"},
    #     "TOSHI": {"toshi", "toshitoken"},
    #     "BASED": {"based", "based token", "based finance"},
    #     "MEM": {"mem", "meme token", "meme coin"},
    #     "PENDLE": {"pendle", "pendle token"},
    #     "DOSU": {"dosu", "dosu token"},
    #     "ABASE": {"abase", "abase token"},
    #     "FXN": {"fxn", "function token", "function x"},
    #     "ECHELON": {"echelon", "echelon prime"},
    #     # Solana Ecosystem Tokens
    #     "SOL": {"solana", "sol"},
    #     "BONK": {"bonk", "bonk token", "bonk coin"},
    #     "RAY": {"raydium", "ray token"},
    #     "SRM": {"serum", "srm token"},
    #     "SAMO": {"samoyedcoin", "samo"},
    #     "ORCA": {"orca", "orca token"},
    #     "STEP": {"step finance", "step"},
    #     "ATLAS": {"star atlas", "atlas token"},
    #     "COPE": {"cope", "cope token"},
    #     # AI Tokens
    #     "AGIX": {"singularitynet", "agix token"},
    #     "OCEAN": {"ocean protocol", "ocean token"},
    #     "FET": {"fetch.ai", "fetch token", "fet token"},
    #     "GRT": {"graph", "graph token"},
    #     "NMR": {"numeraire", "nmr token"},
    #     "RLC": {"iexec", "rlc token"},
    #     "INJ": {"injective", "injective protocol"},
    #     "aixbt": {"aixbt", "virtuals", "AIXBT"},
    #     "ai16z": {"eliza", "elizaos"},
    #     # Major Stablecoins
    #     "USDT": {"tether", "usdt", "tether token"},
    #     "USDC": {"usd coin", "usdc", "circle"},
    #     "DAI": {"dai", "dai stablecoin"},
    #     # Popular DeFi Tokens
    #     "LINK": {"chainlink", "link token", "link"},
    #     "UNI": {"uniswap", "uni token"},
    #     "AAVE": {"aave", "aave token"},
    #     "SNX": {"synthetix", "snx token"},
    #     "CRV": {"curve", "curve dao", "curve token"},
    #     # Meme Coins
    #     "DOGE": {"dogecoin", "doge"},
    #     "SHIB": {"shiba inu", "shib", "shiba"},
    #     "PEPE": {"pepe", "pepe coin"},
    #     "FLOKI": {"floki", "floki inu"},
    #     "WOJAK": {"wojak", "wojak coin"},
    #     "SNEK": {"snek", "snek coin"},
    #     # Major Layer 1 Tokens
    #     "ETH": {"ethereum", "ether", "eth"},
    #     "BTC": {"bitcoin", "btc"},
    #     "BNB": {"binance coin", "bnb", "binance token"},
    #     "MATIC": {"polygon", "matic token", "matic"},
    #     "AVAX": {"avalanche", "avax"},
    #     "ARB": {"arbitrum", "arb", "arbitrum token"},
    #     "OP": {"optimism", "op token"},
    #     # GameFi Tokens
    #     "AXS": {"axie infinity", "axs token"},
    #     "SAND": {"sandbox", "sand token"},
    #     "MANA": {"decentraland", "mana token"},
    #     "ILV": {"illuvium", "ilv token"},
    #     # Privacy Tokens
    #     "XMR": {"monero", "xmr"},
    #     "ZEC": {"zcash", "zec"},
    #     "SCRT": {"secret", "secret network", "scrt token"},
    # }

    # @staticmethod
    # def get_chain_mapping():
    #     return {
    #         "eth": {"names": {"ethereum", "eth", "mainnet", "ether"}, "default": True},
    #         "bsc": {
    #             "names": {"binance", "bsc", "bnb", "binance smart chain"},
    #             "default": False,
    #         },
    #         "polygon": {"names": {"polygon", "matic", "pol"}, "default": False},
    #         "avalanche": {
    #             "names": {"avalanche", "avax", "avax c-chain"},
    #             "default": False,
    #         },
    #         "arbitrum": {
    #             "names": {"arbitrum", "arb", "arbitrum one"},
    #             "default": False,
    #         },
    #         "base": {
    #             "names": {"base", "basechain"},
    #             "default": False,
    #         },
    #     }

from moralis import evm_api
from app.api.client.api_client import ApiClient


class TokenApiClient(ApiClient):

    def get_token_metadata(self, params: dict):
        """Get token metadata from Moralis API."""
        return evm_api.token.get_token_metadata(
            api_key=self.api_key,
            params=params
        )
    
    def get_token_metadata_by_symbol(self, params: dict):
        """Get token metadata from Moralis API."""
        return evm_api.token.get_token_metadata_by_symbol(
            api_key=self.api_key,
            params=params
        )
    
    def get_token_owners(self, params: dict) -> dict:
        """Get token owners from Moralis API."""
        return evm_api.token.get_token_owners(
                api_key=self.api_key,
                params=params
                )
    
    def get_token_price(self, params: dict) -> dict:
        """Get token price from Moralis API."""
        return evm_api.token.get_token_price(
            api_key=self.api_key,
            params=params
        )
    
    def get_top_profitable_wallet_per_token(self, params: dict) -> dict:
        """Get top wallets for token from Moralis API."""
        return evm_api.token.get_top_profitable_wallet_per_token(
            api_key=self.api_key,
            params=params
        )
    
    def get_wallet_active_chains(self, params: dict) -> dict:
        """Get wallet active chains from Moralis API."""
        return evm_api.wallets.get_wallet_active_chains(
            api_key=self.api_key,
            params=params
            )
    
    def get_token_stats(self, params: dict) -> dict:
        """Get token stats from Moralis API."""
        return evm_api.token.get_token_stats(
            api_key=self.api_key,
            params=params
            )
    
    def get_token_transfers(self, params: dict) -> dict:
        """Get token transfers from Moralis API."""
        return evm_api.token.get_token_transfers(
            api_key=self.api_key,
            params=params
            )
    
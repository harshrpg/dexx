from app.api.client.api_client import ApiClient
from moralis import evm_api


class WalletApiClient(ApiClient):
    """WalletApi
    This is the main class for WalletApi.
    """

    def get_wallet_token_transfers(self, params: dict) -> dict:
        """Get wallet token transfers from client"""
        if (self.__check_api_key__()):
            return evm_api.token.get_wallet_token_transfers(
                api_key=self.api_key,
                params=params
            )
        else:
            raise ValueError("Client's Api Key not set")
            
    # def get_wallet_history(self, params: dict) -> dict:
    #     """Get wallet transaction history"""
    #     if (self.__check_api_key__()):
    #         return evm_api.wallets.get_wallet_history(
    #             api_key=self.api_key,
    #             params=params
    #         )
    #     else:
    #         raise ValueError("Client's Api Key not set")
    
    # def get_wallet_token_balances_price(self, params: dict) -> dict:
    #     """Get wallet token balances price"""
    #     if (self.__check_api_key__()):
    #         return evm_api.wallets.get_wallet_token_balances_price(
    #             api_key=self.api_key,
    #             params=params
    #         )
    #     else:
    #         raise ValueError("Client's Api Key not set")
        
    # def get_wallet_profitability_summary(self, params: dict) -> dict:
    #     """Get wallet PnL price"""
    #     if (self.__check_api_key__()):
    #         return evm_api.wallets.get_wallet_profitability_summary(
    #             api_key=self.api_key,
    #             params=params
    #         )
    #     else:
    #         raise ValueError("Client's Api Key not set")

    def __check_api_key__(self) -> bool:
        if self.api_key is not None or self.api_key != "":
            return True
        return False

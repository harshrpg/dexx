import pytest

from app.api.client.mobula.metacore_client import MetacoreClient
from app.models.token_symbols import GetAllCryptocurrencies_Mobula_Data


@pytest.mark.integration  # Mark as integration test
class TestMetacoreClientIntegration:

    def test_get_all_cryptocurrencies_live(self):
        """Test actual API call to get cryptocurrencies"""
        # Make the actual API call
        client = MetacoreClient()
        response = client.get_all_cryptocurrencies()

        # Basic response validation
        assert isinstance(response, dict)
        assert "data" in response
        assert len(response["data"]) > 0

        # Validate response structure using Pydantic model
        validated_data = GetAllCryptocurrencies_Mobula_Data.model_validate(response)

        # Check first few items have required fields
        for crypto in validated_data.data[:5]:  # Check first 5 items
            assert isinstance(crypto.id, int)
            assert isinstance(crypto.name, str)
            assert isinstance(crypto.symbol, str)
            assert len(crypto.symbol) > 0

        # Check for specific known cryptocurrencies (adjust based on your needs)
        symbols = {crypto.symbol for crypto in validated_data.data}
        common_symbols = {"BTC", "ETH", "USDT", "BNB"}
        assert any(
            symbol in symbols for symbol in common_symbols
        ), "No common cryptocurrencies found"

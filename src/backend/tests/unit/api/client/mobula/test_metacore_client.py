import pytest
import requests
import requests_mock
from app.api.client.mobula.metacore_client import MetacoreClient
from app.core.config import settings
from app.models.api.routes import MobulaEndpoints
from app.models.token_symbols import GetAllCryptocurrencies_Mobula_Data


class TestMetacoreClient:
    @pytest.fixture
    def mock_crypto_response(self):
        return {
            "data": [
                {"id": 2, "name": "LYS Capital", "symbol": "LYS"},
                {"id": 3, "name": "StaySAFU", "symbol": "SAFU"},
                {"id": 4, "name": "Fold", "symbol": "FLD"},
            ]
        }

    def test_get_all_cryptocurrencies_success(self, mock_crypto_response):
        with requests_mock.Mocker() as m:
            # Construct expected URL
            expected_url = f"{settings.MOBULA_PRODUCTION_API_ENDPOINT}/{MobulaEndpoints.REST_API}/{MobulaEndpoints.REST_API_VERSION}/{MobulaEndpoints.GET_ALL_CRYPTOCURRENCIES}"
            print(expected_url)
            # Mock the API response
            m.get(expected_url, json=mock_crypto_response)

            # Make the call
            metacore_client = MetacoreClient()
            response = metacore_client.get_all_cryptocurrencies()

            # Verify the response
            assert response == mock_crypto_response
            assert isinstance(response, dict)
            assert "data" in response
            assert len(response["data"]) == 3

            # Validate response structure
            validated_response = GetAllCryptocurrencies_Mobula_Data.model_validate(
                response
            )
            assert len(validated_response.data) == 3
            assert validated_response.data[0].name == "LYS Capital"
            assert validated_response.data[1].symbol == "SAFU"
            assert validated_response.data[2].id == 4

    def test_get_all_cryptocurrencies_error(self):
        metacore_client = MetacoreClient()
        with requests_mock.Mocker() as m:
            expected_url = f"{settings.MOBULA_PRODUCTION_API_ENDPOINT}/api/1/all"

            # Mock error response
            m.get(
                expected_url, status_code=500, json={"error": "Internal Server Error"}
            )

            # Test error handling
            with pytest.raises(requests.exceptions.HTTPError):
                metacore_client.get_all_cryptocurrencies()

    def test_get_all_cryptocurrencies_connection_error(self):
        metacore_client = MetacoreClient()
        with requests_mock.Mocker() as m:
            expected_url = f"{settings.MOBULA_PRODUCTION_API_ENDPOINT}/api/1/all"

            # Mock connection error
            m.get(expected_url, exc=requests.exceptions.ConnectionError)

            # Test connection error handling
            with pytest.raises(requests.exceptions.ConnectionError):
                metacore_client.get_all_cryptocurrencies()

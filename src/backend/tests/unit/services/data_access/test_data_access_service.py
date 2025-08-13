import pytest
from unittest.mock import Mock, patch
import requests
from app.services.data_access.data_access_service import DataAccessService
from app.models.prompt_analysis import TokenResponse, TokenData


@pytest.fixture
def mock_token_data():
    """Fixture for sample token data"""
    return {
        "data": {
            "id": 1,
            "name": "Test Token",
            "symbol": "TEST",
            "contracts": ["0x123", "0x456"],
            "blockchains": ["ethereum", "bsc"],
            "decimals": [18, 18],
            "twitter": "test_twitter",
            "website": "test.com",
            "logo": "test_logo.png",
            "price": 1.0,
            "market_cap": 1000000.0,
            "liquidity": 500000.0,
            "volume": 100000.0,
            "description": "Test token description",
            "kyc": "verified",
            "audit": "audited",
            "total_supply_contracts": ["0x123"],
            "total_supply": 1000000.0,
            "circulating_supply": 900000,
            "circulating_supply_addresses": ["0x789"],
            "discord": "test_discord",
            "max_supply": 1000000,
            "chat": "test_chat",
            "tags": ["defi"],
            "investors": [],
            "distribution": [],
            "release_schedule": [],
            "cexs": [],
            "listed_at": "2024-01-01T00:00:00Z"
        }
    }


@pytest.fixture
def service_with_mocked_client(mock_token_data):
    """Fixture for DataAccessService with mocked client"""
    with patch('app.services.data_access.data_access_service.MetacoreClient') as MockClient:
        # Create mock instance
        mock_instance = Mock()
        mock_instance.get_metadata.return_value = mock_token_data
        MockClient.return_value = mock_instance
        
        # Create service
        service = DataAccessService()
        return service, mock_instance


class TestDataAccessService:
    """Test suite for DataAccessService"""

    def test_init(self):
        """Test service initialization"""
        service = DataAccessService()
        assert service.mobula_client is not None

    def test_build_query_string_contract_address(self):
        """Test query string building with contract address"""
        service = DataAccessService()
        query = service._build_query_string(
            token_query="ignored",
            contract_address="0x123",
            chain="ethereum",
            token_symbol="ignored"
        )
        assert query == {"asset": "0x123", "blockchain": "ethereum"}

    def test_build_query_string_token_symbol(self):
        """Test query string building with token symbol"""
        service = DataAccessService()
        query = service._build_query_string(
            token_query="ignored",
            contract_address=None,
            chain="ethereum",
            token_symbol="TEST"
        )
        assert query == {"token_symbol": "TEST", "blockchain": "ethereum"}

    def test_build_query_string_token_query(self):
        """Test query string building with general query"""
        service = DataAccessService()
        query = service._build_query_string(
            token_query="test token",
            contract_address=None,
            chain=None,
            token_symbol=None
        )
        assert query == {"asset": "test token"}

    def test_build_query_string_empty(self):
        """Test query string building with no parameters"""
        service = DataAccessService()
        query = service._build_query_string(None, None, None, None)
        assert query == {}

    def test_filter_metadata_with_chain(self, mock_token_data):
        """Test metadata filtering with chain parameter"""
        service = DataAccessService()
        metadata = TokenResponse.model_validate(mock_token_data)
        
        service._filter_metadata(metadata, "ethereum")
        
        assert len(metadata.data.contracts) == 1
        assert metadata.data.contracts[0] == "0x123"
        assert metadata.data.blockchains[0] == "ethereum"
        assert metadata.data.decimals[0] == 18

    def test_filter_metadata_without_chain(self, mock_token_data):
        """Test metadata filtering without chain parameter"""
        service = DataAccessService()
        metadata = TokenResponse.model_validate(mock_token_data)
        
        service._filter_metadata(metadata, None)
        
        assert len(metadata.data.contracts) == 1
        assert metadata.data.contracts[0] == "0x123"
        assert metadata.data.blockchains[0] == "ethereum"
        assert metadata.data.decimals[0] == 18

    def test_fetch_metadata_success(self, service_with_mocked_client, mock_token_data):
        """Test successful metadata fetching"""
        service, mock_instance = service_with_mocked_client

        result = service.fetch_metadata(token_symbol="TEST")

        assert result is not None
        assert isinstance(result, TokenResponse)
        assert result.data.symbol == "TEST"
        mock_instance.get_metadata.assert_called_once_with({"token_symbol": "TEST"})

    def test_fetch_metadata_no_criteria(self, service_with_mocked_client):
        """Test metadata fetching with no search criteria"""
        service, _ = service_with_mocked_client
        with pytest.raises(ValueError) as exc_info:
            service.fetch_metadata()
        assert str(exc_info.value) == "At least one search criteria must be provided"

    def test_fetch_metadata_api_error(self, service_with_mocked_client):
        """Test metadata fetching with API error"""
        service, mock_instance = service_with_mocked_client
        mock_instance.get_metadata.side_effect = requests.exceptions.HTTPError(
            "400 Client Error: Bad Request"
        )

        with pytest.raises(ValueError) as exc_info:
            service.fetch_metadata(token_symbol="TEST")
        assert "Failed to fetch or process metadata" in str(exc_info.value)

    def test_fetch_metadata_invalid_response(self, service_with_mocked_client):
        """Test metadata fetching with invalid response format"""
        service, mock_instance = service_with_mocked_client
        mock_instance.get_metadata.return_value = {"invalid": "data"}

        with pytest.raises(ValueError) as exc_info:
            service.fetch_metadata(token_symbol="TEST")
        assert "Failed to fetch or process metadata" in str(exc_info.value)

    def test_fetch_metadata_empty_response(self, service_with_mocked_client):
        """Test metadata fetching with empty response"""
        service, mock_instance = service_with_mocked_client
        mock_instance.get_metadata.return_value = {"data": None}

        result = service.fetch_metadata(token_symbol="TEST")
        assert result is None 
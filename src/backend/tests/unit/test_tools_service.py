from pydantic import ValidationError
import pytest
import logging
from unittest.mock import Mock, patch
from openai.types.responses import ResponseFunctionToolCall
from app.services.reasoning.tools_service import ToolsService
from app.services.reasoning.constants import FUNCTION_CALL_TYPE, ASSETS

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@pytest.fixture
def mock_data_processing_service():
    logger.debug("Setting up mock_data_processing_service")
    with patch('app.services.reasoning.tools_service.DataProcessingService', autospec=True) as mock:
        mock_instance = mock.return_value
        mock_instance.fetch_token_data_and_process.return_value = {
            "token_metadata": "Test Metadata",
            "ohlcv_data": "Test OHLCV",
            "market_indicators": "Test Indicators",
            "sentiments": "Test Sentiments"
        }
        mock_instance.fetch_latest_tokens.return_value = ["BTC", "ETH"]
        logger.debug("Mock DataProcessingService configured")
        yield mock_instance

@pytest.fixture
def tools_service(mock_data_processing_service):
    logger.debug("Creating ToolsService instance")
    service = ToolsService()
    logger.debug("ToolsService instance created")
    return service

def test_process_tools_with_valid_function_call(tools_service, mock_data_processing_service):
    logger.debug("Starting test_process_tools_with_valid_function_call")
    # Arrange
    tool_response = ResponseFunctionToolCall(
        type=FUNCTION_CALL_TYPE,
        name="get_crypto_data_market_indicators_sentiments",
        arguments='{"assets": ["BTC", "ETH"]}',
        call_id="test-call-id"
    )
    logger.debug(f"Created tool response: {tool_response}")

    # Act
    logger.debug("Calling process_tools")
    result = tools_service.process_tools(tool_response)
    logger.debug(f"Process tools result: {result}")

    # Assert
    logger.debug("Starting assertions")
    assert result is not None
    assert len(result) == 2
    assert result[0]["asset"] == "BTC"
    assert result[1]["asset"] == "ETH"
    mock_data_processing_service.fetch_token_data_and_process.assert_called()
    # Verify the mock was called with the correct arguments
    mock_data_processing_service.fetch_token_data_and_process.assert_any_call(token_symbol="BTC")
    mock_data_processing_service.fetch_token_data_and_process.assert_any_call(token_symbol="ETH")
    logger.debug("All assertions passed")

def test_process_tools_with_empty_assets(tools_service, mock_data_processing_service):
    logger.debug("Starting test_process_tools_with_empty_assets")
    # Arrange
    tool_response = ResponseFunctionToolCall(
        type=FUNCTION_CALL_TYPE,
        name="get_crypto_data_market_indicators_sentiments",
        arguments='{"assets": []}',
        call_id="test-call-id"
    )
    logger.debug(f"Created tool response: {tool_response}")

    # Act
    logger.debug("Calling process_tools")
    result = tools_service.process_tools(tool_response)
    logger.debug(f"Process tools result: {result}")

    # Assert
    logger.debug("Starting assertions")
    assert result == {
        "token_metadata": "Not Available",
        "ohlcv_data": "Not Available",
        "market_indicators": "Not Available",
        "sentiments": "Not Available"
    }
    mock_data_processing_service.fetch_token_data_and_process.assert_not_called()
    logger.debug("All assertions passed")

def test_process_tools_with_invalid_function_call(tools_service):
    logger.debug("Starting test_process_tools_with_invalid_function_call")
    # Arrange
    with pytest.raises(ValidationError) as exc_info:
        tool_response = ResponseFunctionToolCall(
            type="invalid_type", 
            name="get_crypto_data_market_indicators_sentiments",
            arguments='{"assets": ["BTC"]}',
            call_id="test-call-id"
        )
    
    # Assert
    logger.debug("Starting assertions")
    assert "Input should be 'function_call'" in str(exc_info.value)
    assert "type=literal_error" in str(exc_info.value)
    logger.debug("All assertions passed")

def test_process_tools_with_get_latest_tokens(tools_service, mock_data_processing_service):
    logger.debug("Starting test_process_tools_with_get_latest_tokens")
    # Arrange
    tool_response = ResponseFunctionToolCall(
        type=FUNCTION_CALL_TYPE,
        name="get_latest_tokens",
        arguments='{}',
        call_id="test-call-id"
    )
    logger.debug(f"Created tool response: {tool_response}")

    # Act
    logger.debug("Calling process_tools")
    result = tools_service.process_tools(tool_response)
    logger.debug(f"Process tools result: {result}")

    # Assert
    logger.debug("Starting assertions")
    assert result == ["BTC", "ETH"]
    mock_data_processing_service.fetch_latest_tokens.assert_called_once()
    logger.debug("All assertions passed")

def test_process_tools_with_invalid_arguments(tools_service):
    # Arrange
    tool_response = ResponseFunctionToolCall(
        type=FUNCTION_CALL_TYPE,
        name="get_crypto_data_market_indicators_sentiments",
        arguments='{"invalid_key": ["BTC"]}',
        call_id="test-call-id"
    )

    # Act
    result = tools_service.process_tools(tool_response)

    # Assert
    assert result is None

def test_process_tools_with_exception(tools_service, mock_data_processing_service):
    # Arrange
    mock_data_processing_service.fetch_token_data_and_process.side_effect = Exception("Test error")
    tool_response = ResponseFunctionToolCall(
        type=FUNCTION_CALL_TYPE,
        name="get_crypto_data_market_indicators_sentiments",
        arguments='{"assets": ["BTC"]}',
        call_id="test-call-id"
    )

    # Act
    result = tools_service.process_tools(tool_response)

    # Assert
    assert result is not None
    assert result[0]["asset"] == "BTC"
    assert result[0]["data"] == {
        "token_metadata": "Not Available",
        "ohlcv_data": "Not Available",
        "market_indicators": "Not Available",
        "sentiments": "Not Available"
    } 
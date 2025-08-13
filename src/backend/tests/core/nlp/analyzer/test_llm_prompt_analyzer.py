import pytest
from unittest.mock import Mock, patch
from app.core.nlp.analyzer.llm_prompt_analyzer import LLMPromptAnalyzer, PromptAnalysisResult

@pytest.fixture
def llm_analyzer():
    return LLMPromptAnalyzer()

@pytest.fixture
def mock_openai_client():
    with patch('app.core.nlp.analyzer.llm_prompt_analyzer.OpenAiAPIClient') as mock:
        client = Mock()
        mock.return_value = client
        yield client

@pytest.mark.asyncio
async def test_session_context_flow(llm_analyzer, mock_openai_client):
    """Test the complete flow of session context handling"""
    
    # Test Case 1: General Query
    mock_openai_client.system_query.return_value.content = '''
    {
        "token_symbol": null,
        "token_name": null,
        "chain": null,
        "intent": "General blockchain question",
        "action": null,
        "parameters": {},
        "confidence": 0.9,
        "is_followup": false,
        "query_type": "general_query"
    }
    '''
    
    result = await llm_analyzer.analyze_prompt(
        "What is blockchain technology?",
        chat_history=[]
    )
    
    assert result.query_type == "general_query"
    assert result.token_symbol is None
    assert result.is_followup is False
    
    # Test Case 2: Token Action (New Token)
    mock_openai_client.system_query.return_value.content = '''
    {
        "token_symbol": "ETH",
        "token_name": "Ethereum",
        "chain": "ethereum",
        "intent": "Get token price information",
        "action": "get_token_price",
        "parameters": {
            "chain": "ethereum",
            "token_address": "0x..."
        },
        "confidence": 0.95,
        "is_followup": false,
        "query_type": "token_action"
    }
    '''
    
    result = await llm_analyzer.analyze_prompt(
        "What is the price of ETH?",
        chat_history=[{
            "role": "user",
            "content": "What is blockchain technology?"
        }]
    )
    
    assert result.query_type == "token_action"
    assert result.token_symbol == "ETH"
    assert result.is_followup is False
    
    # Test Case 3: Follow-up Question
    mock_openai_client.system_query.return_value.content = '''
    {
        "token_symbol": "ETH",
        "token_name": "Ethereum",
        "chain": "ethereum",
        "intent": "Get token volume information",
        "action": "get_token_stats",
        "parameters": {
            "chain": "ethereum",
            "token_address": "0x..."
        },
        "confidence": 0.95,
        "is_followup": true,
        "query_type": "context_action"
    }
    '''
    
    result = await llm_analyzer.analyze_prompt(
        "What about its volume?",
        chat_history=[
            {"role": "user", "content": "What is blockchain technology?"},
            {"role": "user", "content": "What is the price of ETH?"}
        ]
    )
    
    assert result.query_type == "context_action"
    assert result.token_symbol == "ETH"
    assert result.is_followup is True
    
    # Test Case 4: New Token Action
    mock_openai_client.system_query.return_value.content = '''
    {
        "token_symbol": "BTC",
        "token_name": "Bitcoin",
        "chain": "bitcoin",
        "intent": "Get token price information",
        "action": "get_token_price",
        "parameters": {
            "chain": "bitcoin",
            "token_address": "0x..."
        },
        "confidence": 0.95,
        "is_followup": false,
        "query_type": "token_action"
    }
    '''
    
    result = await llm_analyzer.analyze_prompt(
        "What is the price of BTC?",
        chat_history=[
            {"role": "user", "content": "What is blockchain technology?"},
            {"role": "user", "content": "What is the price of ETH?"},
            {"role": "user", "content": "What about its volume?"}
        ]
    )
    
    assert result.query_type == "token_action"
    assert result.token_symbol == "BTC"
    assert result.is_followup is False
    
    # Test Case 5: General Query
    mock_openai_client.system_query.return_value.content = '''
    {
        "token_symbol": null,
        "token_name": null,
        "chain": null,
        "intent": "General blockchain question",
        "action": null,
        "parameters": {},
        "confidence": 0.9,
        "is_followup": false,
        "query_type": "general_query"
    }
    '''
    
    result = await llm_analyzer.analyze_prompt(
        "How does mining work?",
        chat_history=[
            {"role": "user", "content": "What is blockchain technology?"},
            {"role": "user", "content": "What is the price of ETH?"},
            {"role": "user", "content": "What about its volume?"},
            {"role": "user", "content": "What is the price of BTC?"}
        ]
    )
    
    assert result.query_type == "general_query"
    assert result.token_symbol is None
    assert result.is_followup is False

@pytest.mark.asyncio
async def test_token_discovery_queries(llm_analyzer, mock_openai_client):
    """Test handling of token discovery queries"""
    
    # Test Case: Top Meme Coins Query
    mock_openai_client.system_query.return_value.content = '''
    {
        "token_symbol": "DOGE",
        "token_name": "Dogecoin",
        "chain": "ethereum",
        "intent": "Find top meme coin",
        "action": "get_token_metadata",
        "parameters": {
            "chain": "ethereum",
            "token_address": "0x..."
        },
        "confidence": 0.95,
        "is_followup": false,
        "query_type": "token_action"
    }
    '''
    
    result = await llm_analyzer.analyze_prompt(
        "What are the top meme coins to invest in?",
        chat_history=[]
    )
    
    assert result.query_type == "token_action"
    assert result.token_symbol == "DOGE"
    assert result.is_followup is False
    assert result.action == "get_token_metadata"

@pytest.mark.asyncio
async def test_follow_up_with_different_token(llm_analyzer, mock_openai_client):
    """Test that mentioning a different token makes it a new token action"""
    
    # First query about ETH
    mock_openai_client.system_query.return_value.content = '''
    {
        "token_symbol": "ETH",
        "token_name": "Ethereum",
        "chain": "ethereum",
        "intent": "Get token price information",
        "action": "get_token_price",
        "parameters": {
            "chain": "ethereum",
            "token_address": "0x..."
        },
        "confidence": 0.95,
        "is_followup": false,
        "query_type": "token_action"
    }
    '''
    
    result = await llm_analyzer.analyze_prompt(
        "What is the price of ETH?",
        chat_history=[]
    )
    
    assert result.token_symbol == "ETH"
    assert result.is_followup is False
    
    # Follow-up mentioning a different token (BTC)
    mock_openai_client.system_query.return_value.content = '''
    {
        "token_symbol": "BTC",
        "token_name": "Bitcoin",
        "chain": "bitcoin",
        "intent": "Get token price information",
        "action": "get_token_price",
        "parameters": {
            "chain": "bitcoin",
            "token_address": "0x..."
        },
        "confidence": 0.95,
        "is_followup": false,
        "query_type": "token_action"
    }
    '''
    
    result = await llm_analyzer.analyze_prompt(
        "What about BTC?",
        chat_history=[{
            "role": "user",
            "content": "What is the price of ETH?"
        }]
    )
    
    assert result.token_symbol == "BTC"
    assert result.is_followup is False  # Should be False because it's a different token
    assert result.query_type == "token_action" 
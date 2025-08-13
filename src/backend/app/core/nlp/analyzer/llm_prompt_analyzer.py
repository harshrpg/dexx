import os
from typing import Optional, Dict, List
import json
from pydantic import BaseModel
import logging

from openai import OpenAI

from dotenv import load_dotenv
load_dotenv()


# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

from app.api.client.openai.openai_api_client import OpenAiAPIClient
from app.core.nlp.parser.keyword_mappings import KeywordMappings


class PromptAnalysisResult(BaseModel):
    token_symbol: Optional[str]
    token_name: Optional[str]
    chain: Optional[str]
    action: Optional[str]
    parameters: Dict[str, Optional[str]]
    confidence: float
    is_followup: bool
    query_type: str  # token_action, context_action, or general_query


class LLMPromptAnalyzer:
    def __init__(self):
        self.client = OpenAiAPIClient(api_key=os.getenv("OPENAI_API_KEY"))
        self.mappings = KeywordMappings()
        self.logger = logging.getLogger(__name__)

        # Available actions that we support
        self.available_actions = {
            "get_token_transfers": {
                "description": "Get transfer history of a token",
                "required_params": ["token_address", "chain"],
            },
            "get_token_metadata": {
                "description": "Get token information (name, symbol, decimals, etc)",
                "required_params": ["token_address", "chain"],
            },
            "get_token_price": {
                "description": "Get current price of a token",
                "required_params": ["token_address", "chain"],
            },
            "get_token_holders": {
                "description": "Get list of token holders",
                "required_params": ["token_address", "chain"],
            },
        }

    def _create_system_prompt(self, prompt: str, chat_history: Optional[List[Dict]] = None) -> str:
        self.logger.info(f"Creating system prompt for query: {prompt[:50]}...")
        actions_list = []
        for action, details in self.mappings.action_mappings.items():
            
            # Get primary keywords as a comma-separated string
            primary_keywords = ", ".join(details["primary"])

            # Get context keywords if they exist
            context_str = ""
            if "context" in details:
                context_keywords = ", ".join(details["context"])
                context_str = f"\n     Context words: {context_keywords}"

            # Get attribute keywords if they exist
            attributes_str = ""
            if "attributes" in details:
                attribute_keywords = ", ".join(details["attributes"])
                attributes_str = f"\n     Related attributes: {attribute_keywords}"

            # Build the complete action description
            action_desc = (
                f"- {action}:\n"
                f"     Description: {details['description']}\n"
                f"     Key terms: {primary_keywords}"
                f"{context_str}"
                f"{attributes_str}\n"
                f"     Required parameters: {', '.join(details['required_params'])}"
            )
            actions_list.append(action_desc)

        # Join all action descriptions
        actions_str = "\n".join(actions_list)

        # Add chat history context if available
        chat_history_str = ""
        if chat_history:
            chat_history_str = "\nPrevious conversation:\n"
            for msg in chat_history[-5:]:  # Use last 5 messages for context
                chat_history_str += f"{msg['role'].title()}: {msg['content']}\n"

        return f"""You are a Web3 prompt analyzer. Your task is to analyze user queries about cryptocurrencies and blockchain.
                    Process the user's prompt and identify the following components:

                    1. Token Identification:
                    - Determine if this is a new token query or a follow-up to a previous token
                    - For new tokens:
                      * Look for explicit token mentions (e.g., $ETH, $BTC)
                      * Look for token names in context (e.g., "ethereum" means ETH)
                      * Extract both symbol and full name
                      * For token discovery queries (e.g., "top meme coins", "best AI tokens"):
                        - Look up the most relevant token based on the query
                        - Return ONLY ONE token that best matches the criteria
                        - Include market data and recent performance
                        - Set query_type to "token_action"
                    - For follow-up questions:
                      * Check if the query references a previous token
                      * If no new token is mentioned, use the token from chat history
                      * Set is_followup to true only if it's a genuine follow-up

                    2. Chain Identification:
                    - Extract blockchain network if mentioned
                    - Common chains: ethereum (eth), binance smart chain (bsc/bnb), polygon (matic), avalanche (avax), arbitrum (arb), base
                    - For follow-up questions, use chain from history if no new chain mentioned

                    3. Intent & Action Analysis:
                    - Identify the user's intent (new token analysis or follow-up)
                    - Map to appropriate action based on intent
                    - Required actions for different intents:
                      * New token queries: get_token_metadata, get_token_price
                      * Follow-up questions: Use context-appropriate action
                      * General queries: No specific action required
                    - For token discovery queries:
                      * Use get_token_metadata to fetch comprehensive token information
                      * Include market data, social metrics, and recent news
                      * Focus on the specific category mentioned (meme, AI, DeFi, etc.)

                    4. Query Type Classification:
                    - token_action: New token analysis request or token discovery
                    - context_action: Follow-up to previous token
                    - general_query: General blockchain/crypto questions

                    Available Actions and their description:
                    {actions_str}
                    
                    <chat_history>
                    {chat_history_str}
                    </chat_history>

                    Respond in JSON format:
                    {{
                        "token_symbol": "symbol or null",
                        "token_name": "full name or null",
                        "chain": "chain name or null",
                        "intent": "brief description of user's intent",
                        "action": "matching action from available actions",
                        "parameters": {{
                            "param1": "value1",
                            ...
                        }},
                        "confidence": float between 0 and 1,
                        "is_followup": boolean indicating if this is a follow-up question,
                        "query_type": "token_action|context_action|general_query"
                    }}

                    IMPORTANT: 
                    - For token discovery queries, return ONLY ONE most relevant token
                    - Include market data and recent performance for discovered tokens
                    - Action is REQUIRED if the query matches any action pattern
                    - If the query is not a general query, then the token_symbol is required
                    - For time-related queries, always include time_range in parameters
                    - For follow-up questions, maintain context from previous messages
                    - Set is_followup to true only if it's a genuine follow-up to a previous token
                    - A query is NOT a follow-up if it mentions a different token
                    - Query type should reflect the nature of the request
                    - Include time parameters for time-related queries
                    
                    Now analyze this user query and provide a json response:{prompt}
                    """

    def _format_metadata(self, metadata: Dict) -> str:
        """Format metadata into a readable string"""
        self.logger.debug(f"Formatting metadata: {metadata}")
        parts = []
        if metadata.get("token_symbol"):
            parts.append(f"Token: {metadata['token_symbol']}")
        if metadata.get("chain"):
            parts.append(f"Chain: {metadata['chain']}")
        if metadata.get("action"):
            parts.append(f"Action: {metadata['action']}")
        if metadata.get("is_followup"):
            parts.append("Follow-up question")
        formatted = ", ".join(parts)
        self.logger.debug(f"Formatted metadata: {formatted}")
        return formatted

    def _clean_json_response(self, response: str) -> str:
        """Clean the response to get pure JSON string."""
        try:
            self.logger.debug(f"Cleaning JSON response: {response[:100]}...")
            # Remove markdown code blocks if present
            if response.startswith("```") and response.endswith("```"):
                # Extract content between triple backticks
                response = response.split("```")[1]
                # Remove language identifier if present (e.g., 'json\n')
                if response.startswith("json\n"):
                    response = response[5:]
                elif response.startswith("json"):
                    response = response[4:]

            # Remove any leading/trailing whitespace
            response = response.strip()
            self.logger.debug("JSON response cleaned successfully")
            return response

        except Exception as e:
            self.logger.error(f"Error cleaning JSON response: {str(e)}", exc_info=True)
            raise

    def _transform_response_format(self, raw_response: dict) -> dict:
        """Transform the LLM response format to our expected format."""
        try:
            # Extract basic fields
            transformed = {
                "token_symbol": raw_response.get("token_symbol"),
                "token_name": raw_response.get("token_name"),
                "chain": raw_response.get("chain"),
                "action": raw_response.get("action"),
                "parameters": raw_response.get("parameters", {}),
                "confidence": raw_response.get("confidence", 0.0),
                "is_followup": raw_response.get("is_followup", False),
                "query_type": raw_response.get("query_type", "general_query")
            }

            # Validate query_type
            valid_query_types = ["token_action", "context_action", "general_query"]
            if transformed["query_type"] not in valid_query_types:
                # Determine query type based on other fields
                if transformed["token_symbol"] and not transformed["is_followup"]:
                    transformed["query_type"] = "token_action"
                elif transformed["is_followup"]:
                    transformed["query_type"] = "context_action"
                else:
                    transformed["query_type"] = "general_query"

            return transformed

        except Exception as e:
            self.logger.error(f"Error transforming response format: {str(e)}", exc_info=True)
            raise

    async def analyze_prompt(
        self, 
        prompt: str, 
        chat_history: Optional[List[Dict]] = None
    ) -> PromptAnalysisResult:
        """Analyze a prompt using GPT to extract token, chain, and intent."""
        try:
            self.logger.info(f"Analyzing prompt: {prompt[:50]}...")
            self.logger.debug(f"Chat history length: {len(chat_history) if chat_history else 0}")

            analysis_prompt = self._create_system_prompt(
                prompt=prompt,
                chat_history=chat_history
            )

            self.logger.debug("Sending prompt to LLM for analysis")
            response = self.client.system_query(
                prompt=analysis_prompt,
            )

            # Parse the response
            # Clean the response content
            self.logger.debug("Cleaning LLM response")
            cleaned_json_str = self._clean_json_response(response.content)
            self.logger.debug(f"Cleaned JSON: {cleaned_json_str}")

            # Parse the cleaned JSON
            self.logger.debug("Parsing cleaned JSON")
            raw_result = json.loads(cleaned_json_str)
            self.logger.debug(f"Raw result: {raw_result}")

            # Transform to our expected format
            self.logger.debug("Transforming response format")
            transformed_result = self._transform_response_format(raw_result)
            self.logger.info(f"Analysis complete. Token: {transformed_result.get('token_symbol')}, Follow-up: {transformed_result.get('is_followup')}")

            # Validate and return
            return PromptAnalysisResult(**transformed_result)

        except Exception as e:
            self.logger.error(f"Error in LLM analysis: {str(e)}", exc_info=True)
            raise

    async def validate_analysis(self, analysis: PromptAnalysisResult) -> bool:
        """Validate that the analysis results are consistent with available actions."""
        try:
            self.logger.debug(f"Validating analysis: {analysis}")
            
            # Check if the action exists
            if analysis.action not in self.available_actions:
                self.logger.warning(f"Invalid action: {analysis.action}")
                return False

            # Check if required parameters are present
            required_params = self.available_actions[analysis.action]["required_params"]
            if not all(param in analysis.parameters for param in required_params):
                self.logger.warning(f"Missing required parameters for action {analysis.action}")
                return False

            # Validate confidence
            if not (0 <= analysis.confidence <= 1):
                self.logger.warning(f"Invalid confidence value: {analysis.confidence}")
                return False

            self.logger.info("Analysis validation successful")
            return True

        except Exception as e:
            self.logger.error(f"Error in analysis validation: {str(e)}", exc_info=True)
            return False

import json
import os
from typing import Any, Dict, Optional
from dotenv import load_dotenv
from app.api.client.openai.openai_api_client import OpenAiAPIClient
from app.api.client.cryptopanic.cryptopanic_client import CryptoPanicClient
from app.models.prompt_analysis import ProcessedPrompt
from app.models.response import ResponseType
from app.services.message_service import MessageService
from app.services.data_access.data_access_service import DataAccessService
import logging

load_dotenv()


class InsightService:
    def __init__(self):
        self.client = OpenAiAPIClient(os.getenv("OPENAI_API_KEY"))
        self.message_service = MessageService()
        self.dal_service = DataAccessService()
        self.cryptopanic_client = CryptoPanicClient()
        self.logger = logging.getLogger(__name__)

    def generate(
        self,
        response_data: Dict,
        user_prompt: str,
        wallet_address: str = None,
        session_id: str = None,
    ) -> str:
        try:
            self.logger.info(f"Generating insight for prompt: {user_prompt[:50]}...")
            # Save user message with metadata
            self._save_user_message(
                wallet_address, session_id, user_prompt, response_data
            )

            # Get conversation history and context
            conversation_history = []
            if session_id:
                conversation_history = self.message_service.format_for_chatgpt(session_id)
                session_context = self.message_service.get_session_context(session_id)
                self.logger.debug(f"Retrieved {len(conversation_history)} messages from history")
            else:
                session_context = {}
                self.logger.warning("No session_id provided, proceeding without conversation history")

            # Generate appropriate prompt based on response type
            prompt = self._generate_prompt_by_type(
                response_data, 
                user_prompt,
                session_context
            )

            # Generate insight with context
            self.logger.debug("Sending prompt to LLM for analysis")
            insight = self.client.query(
                prompt=prompt,
                conversation_history=conversation_history
            )

            # Save assistant message
            self._save_assistant_message(wallet_address, session_id, insight.content)
            self.logger.info("Successfully generated and saved insight")
            return insight
        except Exception as e:
            self.logger.error(f"Error generating insight: {str(e)}", exc_info=True)
            return self._generate_error_prompt(str(e))

    def _generate_prompt_by_type(
        self, 
        response_data: Dict, 
        user_prompt: str,
        session_context: Dict
    ) -> str:
        insight_generators = {
            ResponseType.ERROR.value: self._generate_error_prompt,
            ResponseType.NO_WEB3.value: self._generate_non_web3_prompt,
            ResponseType.NO_INTENT.value: self._generate_no_intent_prompt,
            ResponseType.SUCCESS.value: self._generate_web3_prompt,
        }
        generator = insight_generators.get(response_data["type"])
        return generator(response_data=response_data, user_prompt=user_prompt, session_context=session_context)

    def _generate_error_prompt(
        self, response_data: Optional[Dict] = None, user_prompt: Optional[str] = None, session_context: Optional[Dict] = None
    ) -> str:
        return f"""
        I encountered an error while processing your request: {response_data['message']}

        The error occurred when user requested the below prompt
        <user_prompt>
        {user_prompt}
        </user_prompt>

        Explain the relevant error based on the error message
        """

    def _generate_web3_prompt(
        self, 
        response_data: Dict, 
        user_prompt: str,
        session_context: Dict
    ) -> str:
        metadata = response_data.get("metadata", {})
        parsed_results = response_data.get("parsed_results", {})
        data = response_data.get("data", {})

        if not data:
            return self._generate_no_intent_prompt(metadata, user_prompt, session_context)

        action = data.get("endpoints")
        action_data = data[action].get("data") if action in data else None
        params = parsed_results.get("api_calls", {}).get(action, {}).get("params", {})

        # Get context from either current response or session
        context = {
            "token": metadata.get("token_symbol") or session_context.get("last_token"),
            "chain": params.get("chain") or session_context.get("last_chain"),
            "contract": metadata.get("contract_address") or session_context.get("last_contract_address"),
            "token_name": metadata.get("token_name") or session_context.get("last_token_name"),
            "action": action or session_context.get("last_action")
        }

        base_context = self._get_base_context(action, context, params, data)
        return self._create_analysis_prompt(user_prompt, base_context, action_data, session_context)

    def _add_context_to_prompt(self, base_prompt: str, messages: list) -> str:
        """Add conversation history to the prompt"""
        context = "\n\nPrevious conversation:\n"
        for msg in messages[-5:]:  # Use last 5 messages for context
            context += f"{msg['role'].title()}: {msg['content']}\n"

        return f"{context}\nNow, based on this context and the current query:\n{base_prompt}"

    def _generate_raw_prompt(self, user_prompt: str) -> str:
        logging.info("Generating Raw prompt")
        prompt = f"""
        Your personality is of a trading assistant
        Make an best effort response for user's query: 
        {user_prompt} 
        """
        return prompt

    def _generate_non_web3_prompt(
        self, user_prompt: str, response_data: Optional[Dict] = None
    ) -> str:
        example_queries = [
            "Show me the current price of LINK token",
            "Who are the top holders of ETH on ethereum chain?",
            "Get me transfer history of LINK for the last 7 days",
            "Show profitable wallets trading AIXBT token",
        ]
        logging.info("Generating non web3 response")
        prompt = f"""
        {user_prompt} is not directly web3 related. Provide a response in relation to the query but add
        more context below:

        Understand the query and generate an appropriate response, If it is completely out of web3 scope 
        then let them understand that you are Dexx a blockchain analytics agent. You provide quick, responses about blockchain and crypto markets.
        You can aid people in becoming better at their trades.

        It it looks like within web3 scope ask the user if that would like to try with the contract address and make sure they provide what chain the token is on as well.
        e.g., Show top profitable wallets in LINK on eth OR Fetch latest transfers on AIXBT on base

        If it is finance related then come up with a related response.

        Dexx is specialized in:
        - Token price analysis
        - Holder distribution analysis
        - Transfer pattern analysis
        - Profitable wallet identification

        Make it clear that Dexx only supports EVM API tokens. Solana support is coming soon. 
        
        Here are some example queries you can try:
        {', '.join(f'"{q}"' for q in example_queries)}
        
        Please provide a blockchain-related query using either a token symbol (like ETH, LINK) or a contract address (0x...).
        """

        return prompt

    def _get_base_context(
        self,
        action: str,
        context: Dict[str, Any],
        params: Dict[str, Any],
        action_result: Dict[str, Any],
    ) -> str:
        """Get base context with safe parameter access and fallback values"""
        token_name = context.get("token_name", "Unknown Token")
        token_symbol = context.get("token", "")
        chain = context.get("chain", "unknown chain")

        context_builders = {
            "get_token_owners": lambda: (
                f"Token: {token_name} ({token_symbol}) on {chain}"
            ),
            "get_token_price": lambda: (
                f"Current price data for {token_name} on {chain}"
            ),
            "get_top_profitable_wallet_per_token": lambda: (
                f"Profitable wallets for {token_name} over "
                f"{params.get('days', 'recent')} days"
            ),
            "get_wallet_active_chains": lambda: (
                f"Chain activity for wallet "
                f"{params.get('address', 'unknown wallet')}"
            ),
            "get_token_stats": lambda: (
                f"Statistics for {token_name}"
                f"{' over ' + params['timeframe'] if 'timeframe' in params else ''}"
            ),
            "get_token_transfers": lambda: (
                f"Transfer activity for {token_name}"
                f"{' from ' + params.get('from_date', '') if 'from_date' in params else ''}"
                f"{' to ' + params.get('to_date', '') if 'to_date' in params else ''}"
            ),
        }

        try:
            return context_builders.get(action, lambda: f"Analysis for {action}")()
        except Exception as e:
            return f"Error occurred {e} while analysing for {token_name} on {chain}"

    def _create_analysis_prompt(
        self, 
        user_prompt: str, 
        base_context: str, 
        action_data: Optional[dict],
        session_context: Optional[Dict] = None
    ) -> str:
        """Create a structured analysis prompt combining user query, context, and data"""
        prompt = f"""
        Based on the following context and data, provide a detailed analysis:

        Context: {base_context}
        User Query: {user_prompt}
        """

        if session_context:
            prompt += f"""
            Previous Context:
            - Last Token: {session_context.get('last_token', 'None')}
            - Last Chain: {session_context.get('last_chain', 'None')}
            - Last Action: {session_context.get('last_action', 'None')}
            """

        if action_data:
            prompt += f"""
            Data Analysis:
            {json.dumps(action_data, indent=2)}

            Please analyze this data and provide:
            1. Key insights and patterns
            2. Notable metrics and trends
            3. Relevant implications
            4. Actionable observations

            Focus on the specific aspects mentioned in the user's query while leveraging the provided data.
            """
        else:
            prompt += """
            No specific data is available, but I'll analyze based on the context and query.
            Please provide:
            1. General insights related to the query
            2. Relevant considerations
            3. Suggested next steps or additional data that might be helpful
            """

        return prompt

    def _generate_no_intent_prompt(self, metadata: Dict, user_prompt: str) -> str:
        return f"""
        I understand you're asking about {metadata.get('name', 'this token')} ({metadata.get('symbol', '')}). 
        While I couldn't identify a specific analysis intent from your query "{user_prompt}", 
        here's the basic token information:

        Token Name: {metadata.get('name')}
        Symbol: {metadata.get('symbol')}
        Contract: {metadata.get('address')}
        Decimals: {metadata.get('decimals')}
        
        You can ask about:
        - Current price and market data
        - Token holder distribution
        - Transfer patterns and history
        - Profitable wallet analysis
        
        Please rephrase your query to focus on one of these aspects.
        """

    def _save_user_message(
        self, wallet_address: str, session_id: str, content: str, metadata: Dict = {}
    ):
        try:
            if wallet_address and session_id:
                self.logger.debug(f"Saving user message for session {session_id}")
                self.message_service.save_message(
                    wallet_address=wallet_address,
                    session_id=session_id,
                    content=content,
                    role="user",
                    metadata=metadata,
                )
                self.logger.debug("Successfully saved user message")
            else:
                self.logger.warning("Missing wallet_address or session_id, skipping message save")
        except Exception as e:
            self.logger.error(f"Error saving user message: {str(e)}", exc_info=True)
            raise

    def _save_assistant_message(
        self, wallet_address: str, session_id: str, content: str
    ):
        try:
            if wallet_address and session_id:
                self.logger.debug(f"Saving assistant message for session {session_id}")
                self.message_service.save_message(
                    wallet_address=wallet_address,
                    session_id=session_id,
                    content=content,
                    role="assistant",
                )
                self.logger.debug("Successfully saved assistant message")
            else:
                self.logger.warning("Missing wallet_address or session_id, skipping message save")
        except Exception as e:
            self.logger.error(f"Error saving assistant message: {str(e)}", exc_info=True)
            raise

    def generate_raw(self, user_prompt: str):
        try:
            prompt = self._generate_raw_prompt(user_prompt=user_prompt)
            return self.client.system_query(prompt=prompt)
        except Exception as e:
            return self._generate_error_prompt(str(e))

    def generate_for_processed_prompt(
        self, processed_prompt: ProcessedPrompt, session_id: str, auth_data: Dict = {}
    ):
        try:
            self.logger.info(f"Processing prompt for session {session_id}")
            past_messages = self.message_service.get_session_history(session_id=session_id)
            self.logger.debug(f"Retrieved {len(past_messages)} messages from history")

            metadata = processed_prompt.metadata
            raw_prompt = processed_prompt.prompt_analysis.raw_prompt
            token_data = metadata.data
            
            # Log token data
            self.logger.debug(f"Token: {token_data.name} ({token_data.symbol})")
            self.logger.debug(f"Price: ${token_data.price:.2f}")
            self.logger.debug(f"Market Cap: ${token_data.market_cap:,.2f}")
            self.logger.debug(f"24h Volume: ${token_data.volume:,.2f}")
            self.logger.debug(f"Liquidity: ${token_data.liquidity:,.2f}")

            price = token_data.price
            market_cap = token_data.market_cap
            volume = token_data.volume
            liquidity = token_data.liquidity
            volume_to_mcap = (volume / market_cap) * 100 if market_cap > 0 else 0
            liquidity_to_mcap = (liquidity / market_cap) * 100 if market_cap > 0 else 0

            # Fetch technical analysis data
            # self.logger.info("Fetching technical analysis data")
            # technical_data = self.dal_service.fetch_ohlcv_data(
            #     token_symbol=token_data.symbol,
            #     resolution="1d",
            #     blockchain=token_data.blockchains[0]
            # )
            technical_data = None
            if token_data.blockchains and len(token_data.blockchains) > 0:
                self.logger.info("Fetching technical analysis data")
                try:
                    technical_data = self.dal_service.fetch_ohlcv_data(
                        token_symbol=token_data.symbol,
                        resolution="1d",
                        blockchain=token_data.blockchains[0]
                    )
                except Exception as e:
                    self.logger.warning(f"Failed to fetch technical analysis data: {str(e)}")
            else:
                self.logger.warning("No blockchain information available for technical analysis")

            # Fetch news sentiment
            self.logger.info(f"Fetching news sentiment for {token_data.symbol}")
            try:
                news_data = self.cryptopanic_client.get_news_for_symbol(token_data.symbol)
                sentiment_data = news_data["sentiment"]
                has_sentiment = True
            except Exception as e:
                self.logger.warning(f"Failed to fetch news sentiment: {str(e)}")
                sentiment_data = None
                has_sentiment = False

            # Check if this is a follow-up question
            is_followup = processed_prompt.prompt_analysis.is_followup
            self.logger.info(f"Is follow-up question: {is_followup}")

            if is_followup:
                self.logger.info("Generating concise follow-up response")
                # For follow-up questions, use a more concise prompt
                insight_prompt = f"""You are Dexx, a crypto trading assistant. Provide a concise, focused response to the follow-up question.

Token: {token_data.name} ({token_data.symbol})
Current Price: ${price:.2f}
Market Cap: ${market_cap:,.2f}
24h Volume: ${volume:,.2f}
Liquidity: ${liquidity:,.2f}"""

                if technical_data and "indicators" in technical_data:
                    indicators = technical_data["indicators"]
                    insight_prompt += f"""

Technical Analysis (Based on 7 days of data):
- Trend: {indicators['trend']['direction']} ({indicators['trend']['strength']})
- RSI: {indicators['rsi']['value']:.2f} ({indicators['rsi']['signal']})
- MACD: {indicators['macd']['trend']} with {indicators['macd']['crossover']} crossover
- Bollinger Bands: Price is in {indicators['bollinger_bands']['position']} band
- Moving Averages: MA20=${indicators['moving_averages']['ma20']:.2f}, MA50=${indicators['moving_averages']['ma50']:.2f}, MA200=${indicators['moving_averages']['ma200']:.2f}
- Support/Resistance: Support=${indicators['support_resistance']['support']:.2f}, Resistance=${indicators['support_resistance']['resistance']:.2f}"""

                if has_sentiment:
                    insight_prompt += f"""

Market Sentiment (Based on recent news):
- Overall Sentiment: {sentiment_data['overall'].title()}
- Sentiment Score: {sentiment_data['score']:.2f}
- Bullish News: {sentiment_data['bullish_count']}
- Bearish News: {sentiment_data['bearish_count']}
- Neutral News: {sentiment_data['neutral_count']}"""

                insight_prompt += f"""

User Query: {raw_prompt}

Guidelines for Follow-up Response:
1. Focus ONLY on answering the specific follow-up question
2. Keep the response under 50 words unless more detail is explicitly requested
3. Reference previous context only if directly relevant to the current question
4. Avoid repeating basic token information unless specifically asked
5. Use bullet points for multiple pieces of information
6. If technical analysis or sentiment is requested, focus on the specific indicator or metric asked about
7. Always recommend checking the 1-hour chart for more precise short-term analysis

Example Response Format:
- For price questions: "Current price is $X with Y% 24h change"
- For volume questions: "24h volume is $X with Y% change"
- For technical questions: "Indicator shows X signal (Y value)"
- For trend questions: "Trend is X with Y% change"
- For sentiment: "Market sentiment is X with Y bullish and Z bearish news"

Provide a focused response to the follow-up question.

Note: This analysis is based on 7 days of historical data and should be verified with 1-hour chart analysis for short-term trading decisions. This is not financial advice but an insight. Please do your own research before investing money. As an AI agent, Dexx can make mistakes in analysis and predictions. Always verify critical information independently."""
            else:
                self.logger.info("Generating detailed response for new question")
                # Concise prompt for new questions with technical analysis
                insight_prompt = f"""You are Dexx, a crypto trading assistant. Provide a focused analysis of {token_data.name} ({token_data.symbol}) based on the following data:

Current Price: ${price:.2f}
Market Cap: ${market_cap:,.2f}
24h Volume: ${volume:,.2f}
Liquidity: ${liquidity:,.2f}
Volume/Market Cap: {volume_to_mcap:.2f}%
Liquidity/Market Cap: {liquidity_to_mcap:.2f}%"""

                if technical_data and "indicators" in technical_data:
                    indicators = technical_data["indicators"]
                    insight_prompt += f"""

Technical Analysis (Based on 7 days of data):
- Trend: {indicators['trend']['direction']} ({indicators['trend']['strength']})
- RSI: {indicators['rsi']['value']:.2f} ({indicators['rsi']['signal']})
- MACD: {indicators['macd']['trend']} with {indicators['macd']['crossover']} crossover
- Bollinger Bands: Price is in {indicators['bollinger_bands']['position']} band
- Moving Averages: MA20=${indicators['moving_averages']['ma20']:.2f}, MA50=${indicators['moving_averages']['ma50']:.2f}, MA200=${indicators['moving_averages']['ma200']:.2f}
- Support/Resistance: Support=${indicators['support_resistance']['support']:.2f}, Resistance=${indicators['support_resistance']['resistance']:.2f}

Trading Setup Information:
- Support Level: ${indicators['support_resistance']['support']:.2f} ({(indicators['support_resistance']['distance_to_support'] * 100):.2f}% from current price)
- Resistance Level: ${indicators['support_resistance']['resistance']:.2f} ({(indicators['support_resistance']['distance_to_resistance'] * 100):.2f}% from current price)
- RSI Status: {indicators['rsi']['value']:.2f} ({indicators['rsi']['signal']})
- MACD Signal: {indicators['macd']['trend']} with {indicators['macd']['crossover']} crossover
- Moving Average Alignment: {'Bullish' if indicators['trend']['direction'] == 'bullish' else 'Bearish'} (MA20 > MA50 > MA200)
- Bollinger Band Position: Price is in {indicators['bollinger_bands']['position']} band with {indicators['bollinger_bands']['bandwidth']:.2f}% bandwidth"""

                if has_sentiment:
                    insight_prompt += f"""

Market Sentiment Analysis:
- Overall Market Sentiment: {sentiment_data['overall'].title()}
- Sentiment Score: {sentiment_data['score']:.2f}
- News Distribution:
  * Bullish News: {sentiment_data['bullish_count']}
  * Bearish News: {sentiment_data['bearish_count']}
  * Neutral News: {sentiment_data['neutral_count']}"""

                insight_prompt += f"""

User Query: {raw_prompt}

Guidelines for Response:
1. Focus on answering the specific question about {token_data.symbol}
2. Keep the response under 200 words unless more detail is explicitly requested
3. Include only relevant metrics and data points
4. Use bullet points for multiple pieces of information
5. If technical analysis or sentiment is requested, focus on the specific indicator or metric asked about
6. Avoid generic market education unless specifically asked
7. Consider both technical indicators and market sentiment in your analysis
8. Always recommend checking the 1-hour chart for more precise short-term analysis

Provide a focused analysis.

Note: This analysis is based on 7 days of historical data and should be verified with 1-hour chart analysis for short-term trading decisions. This is not financial advice but an insight. Please do your own research before investing money. As an AI agent, Dexx can make mistakes in analysis and predictions. Always verify critical information independently."""

            self.logger.debug("Sending prompt to LLM for analysis")
            insight = self.client.query(
                prompt=insight_prompt, conversation_history=past_messages
            )
            
            self.logger.debug("Saving assistant message")
            self._save_assistant_message(
                auth_data.get("wallet_address"),
                session_id=session_id,
                content=insight.content,
            )
            self.logger.info("Successfully generated and saved insight")
            return insight
            
        except Exception as e:
            self.logger.error(f"Error in generate_for_processed_prompt: {str(e)}", exc_info=True)
            raise

    def format_number(self, number: float) -> str:
        if number >= 1_000_000_000:
            return f"${number/1_000_000_000:.2f}B"
        elif number >= 1_000_000:
            return f"${number/1_000_000:.2f}M"
        else:
            return f"${number:,.2f}"

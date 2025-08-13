import json
import logging
from typing import Dict
from app.core.nlp.analyzer.llm_prompt_analyzer import LLMPromptAnalyzer
from app.lib.address import extract_contract_address
from app.models.prompt_analysis import (
    Action,
    ActionParameters,
    ChartType,
    PromptAnalysis,
    PromptType,
    TimeFrame,
)
from app.services.message_service import MessageService


class ReasoningService:
    def __init__(self):
        self.llm_analyzer = LLMPromptAnalyzer()
        self.message_service = MessageService()
        self.logger = logging.getLogger(__name__)

    def _determine_chart_type(self, action: str) -> ChartType:
        """Determine appropriate chart type based on action"""
        chart_mappings = {
            "get_token_price": ChartType.LINE,
            "get_token_transfers": ChartType.TABLE,
            "get_token_holders": ChartType.PIE,
            "get_token_metadata": ChartType.TABLE,
        }
        return chart_mappings.get(action, ChartType.NONE)

    async def analyze(self, prompt: str, session_id: str) -> PromptAnalysis:
        try:
            # Get current session context and history
            session_context = self.message_service.get_session_context(session_id)
            session_history = self.message_service.get_session_history(session_id)
            
            # Extract contract address and chain from prompt
            contract_address, chain = extract_contract_address(prompt)
            
            # Analyze prompt with LLM, including chat history
            llm_result = await self.llm_analyzer.analyze_prompt(
                prompt=prompt,
                chat_history=session_history
            )
            
            # Use the query type from LLM analysis
            prompt_type = PromptType(llm_result.query_type)
            context_required = prompt_type in [PromptType.CONTEXT_ACTION, PromptType.GENERAL_QUERY]

            # Update token information if available
            if prompt_type in [PromptType.TOKEN_ACTION, PromptType.CONTEXT_ACTION]:
                token_info = self._get_token_info(
                    llm_result, 
                    contract_address, 
                    chain,
                    session_context
                )
                llm_result.token_symbol = token_info["token_symbol"]
                llm_result.token_name = token_info["token_name"]
                contract_address = token_info["contract_address"]
                chain = token_info["chain"]

            # Create actions if needed
            actions = []
            if llm_result.action:
                chart_type = self._determine_chart_type(llm_result.action)
                action_parameters = self._create_action_parameters(llm_result)
                actions.append(
                    Action(
                        name=llm_result.action,
                        parameters=action_parameters,
                        chart_type=chart_type,
                    )
                )

            # Save message with metadata
            self.message_service.save_message(
                wallet_address="unknown",  # Use real wallet if available
                session_id=session_id,
                content=prompt,
                role="user",
                metadata={
                    "token_symbol": llm_result.token_symbol,
                    "contract_address": contract_address,
                    "chain": chain,
                    "action": llm_result.action,
                    "token_name": llm_result.token_name,
                    "is_followup": llm_result.is_followup,
                    "query_type": llm_result.query_type
                },
            )

            return PromptAnalysis(
                type=prompt_type,
                token_symbol=llm_result.token_symbol,
                token_name=llm_result.token_name,
                chain=chain,
                actions=actions,
                context_required=context_required,
                confidence=llm_result.confidence,
                raw_prompt=prompt,
                contract_address=contract_address,
                is_followup=llm_result.is_followup
            )
        except Exception as e:
            self.logger.error(e)
            raise

    def _determine_prompt_type(
        self, 
        llm_result, 
        contract_address: str, 
        chain: str,
        session_context: dict
    ) -> tuple[PromptType, bool]:
        """Determine prompt type and context requirements"""
        # If it's a follow-up question, use context from previous messages
        if llm_result.is_followup:
            return PromptType.CONTEXT_ACTION, True
            
        if llm_result.token_symbol or contract_address or llm_result.token_name:
            return PromptType.TOKEN_ACTION, False
            
        if (
            session_context.get("last_token")
            or session_context.get("last_contract_address")
            or session_context.get("last_token_name")
        ) and llm_result.action:
            return PromptType.CONTEXT_ACTION, True
            
        return PromptType.GENERAL_QUERY, False

    def _get_token_info(
        self,
        llm_result,
        contract_address: str,
        chain: str,
        session_context: dict
    ) -> dict:
        """Get token information, preferring current prompt over context"""
        # If it's a follow-up question and no new token info is provided, use context
        if llm_result.is_followup and not (llm_result.token_symbol or contract_address):
            return {
                "token_symbol": session_context.get("last_token"),
                "token_name": session_context.get("last_token_name"),
                "contract_address": session_context.get("last_contract_address"),
                "chain": chain or session_context.get("last_chain")
            }
            
        return {
            "token_symbol": llm_result.token_symbol,
            "token_name": llm_result.token_name,
            "contract_address": contract_address,
            "chain": chain
        }

    def _create_action_parameters(self, llm_result) -> ActionParameters:
        """Transform LLM parameters into ActionParameters model"""
        # Extract time frame information
        time_frame = None
        if "time_params" in llm_result.parameters:
            time_params = llm_result.parameters["time_params"]
            if isinstance(time_params, str) and "days" in time_params:
                # Parse "last X days" format
                try:
                    days = int("".join(filter(str.isdigit, time_params)))
                    time_frame = TimeFrame(days=days, from_date=None, to_date=None)
                except ValueError:
                    time_frame = TimeFrame(
                        days=7, from_date=None, to_date=None
                    )  # default
            else:
                time_frame = TimeFrame(days=7, from_date=None, to_date=None)  # default

        # Create ActionParameters
        return ActionParameters(
            chain=llm_result.parameters.get("chain"),
            token_address=None,  # This will be filled later with resolved address
            time_frame=time_frame,
            additional_params={},  # Initialize empty dict for additional params
        )

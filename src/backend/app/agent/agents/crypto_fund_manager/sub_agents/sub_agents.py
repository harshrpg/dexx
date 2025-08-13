from typing import Any
from agents import (
    Agent,
    AgentOutputSchema,
    HandoffInputData,
    ModelSettings,
    RunContextWrapper,
    Tool,
    WebSearchTool,
    function_tool,
    handoff,
)

from app.agent.agents.crypto_fund_manager.tools.tools import Tools
from app.agent.models.models import TokenDataFetchInput, WorkflowContext
from app.agent.utils.custom_agent_hooks import CustomAgentHooks
from app.agent.utils.token_output_schema import TokenOutputSchema
from app.config.agent_lore import (
    DATA_FETCH_AGENT_INSTRUCTIONS,
    DATA_FETCH_AGENT_NAME,
    MODEL,
    REPORTING_AGENT_INSTRUCTIONS,
    REPORTING_AGENT_NAME,
    TRADING_STRATEGIST_INSTRUCTIONS,
    TRADING_STRATEGIST_NAME,
)
from app.models.prompt_analysis import TechincalResponse, TokenResponse

import asyncio

# TODO: Define appropriate output_type(s)
# TODO: Sentiment Data fetch
# TODO: Technical Indicators
# TODO: RAG in the entire workflow

# tools = Tools()


class SubAgents:
    def __init__(self) -> None:
        self.tools = Tools()

    def data_access_agent(self) -> Agent:
        """Creates and returns a data access agent that fetches asset metadata and sentiment in parallel.

        Returns:
            Agent: Configured agent for data access operations
        """

        @function_tool()
        def __fetch_metadata_and_sentiment_in_parallel(
            ctx: RunContextWrapper[WorkflowContext],
            token_data_fetch_input: TokenDataFetchInput,
        ) -> bool:
            """Fetches asset metadata and sentiment data in parallel.

            Args:
                ctx: Run context wrapper
                token_data_fetch_input: Input containing asset name/symbol

            Returns:
                MetaDataAndSentiment: Combined metadata and sentiment data
            """
            try:
                # Validate input
                if not (
                    token_data_fetch_input.asset_name
                    or token_data_fetch_input.asset_symbol
                ):
                    ctx.context.data = None
                    print("No asset name or symbol provided")
                    return False

                # Fetch metadata
                metadata = self.tools.fetch_token_metadata(
                    asset_name=token_data_fetch_input.asset_name,
                    asset_symbol=token_data_fetch_input.asset_symbol,
                )

                if not metadata:
                    ctx.context.data = None
                    print("No metadata found for asset")
                    return False

                # Set asset symbol for parallel fetches
                ctx.context.asset_symbol = (
                    metadata.data.symbol or token_data_fetch_input.asset_symbol
                )
                market = metadata.data.blockchains[0]

                # Fetch sentiment and strategy synchronously
                sentiment = self.tools.fetch_sentiment_for_token(
                    asset_name_or_symbol=ctx.context.asset_symbol
                )

                strategy = self.tools.fetch_strategy_for_token(
                    ctx.context.asset_symbol,
                    market,
                )

                ctx.context.data = TechincalResponse(
                    metadata=metadata, sentiment=sentiment, strategy=strategy
                )

                return bool(ctx.context.data.metadata)

            except Exception as e:
                ctx.context.data = None
                print(f"Error fetching data: {str(e)}")
                return False

        def __filter_input_messages(
            handoff_message_data: HandoffInputData,
        ) -> HandoffInputData:
            """Filters and processes input messages before handoff.

            Args:
                handoff_message_data: Input data to filter

            Returns:
                HandoffInputData: Filtered input data
            """
            return handoff_message_data

        def __on_handoff_to_tsa(
            ctx: RunContextWrapper[WorkflowContext], input: TechincalResponse
        ) -> None:
            print(input)

        return Agent(
            name=DATA_FETCH_AGENT_NAME,
            instructions=DATA_FETCH_AGENT_INSTRUCTIONS,
            output_type=AgentOutputSchema(
                TechincalResponse | None, strict_json_schema=False
            ),
            tools=[__fetch_metadata_and_sentiment_in_parallel],
            model_settings=ModelSettings(tool_choice="required"),
            hooks=CustomAgentHooks(display_name=DATA_FETCH_AGENT_NAME),
            model=MODEL,
        )

    def technical_strategist_agent(self) -> Agent:

        @function_tool(strict_mode=False)
        def __calculate_technical_analysis(
            ctx: RunContextWrapper[WorkflowContext],
        ) -> bool:
            if not ctx.context:
                return False

            if not ctx.context.asset_symbol:
                return False

            if not ctx.context.technical_response:
                return False

            if not ctx.context.technical_response.metadata:
                return False

            if not ctx.context.technical_response.metadata.data:
                return False

            if not ctx.context.technical_response.metadata.data.blockchains:
                return False

            asset_symbol = ctx.context.asset_symbol
            market = ctx.context.technical_response.metadata.data.blockchains[0]

            try:
                strategy = self.tools.fetch_strategy_for_token(
                    asset_symbol,
                    market,
                )
                ctx.context.data.strategy = strategy
                return ctx.context.data.strategy is not None
            except Exception as e:
                print(f"Error calculating technical analysis: {str(e)}")
                return False

        return Agent(
            name=TRADING_STRATEGIST_NAME,
            instructions=TRADING_STRATEGIST_INSTRUCTIONS,
            tools=[__calculate_technical_analysis],
            model_settings=ModelSettings(tool_choice="required"),
        )

    def reporting_agent(self) -> Agent:
        return Agent(
            name=REPORTING_AGENT_NAME, instructions=REPORTING_AGENT_INSTRUCTIONS
        )

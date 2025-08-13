from agents import Agent, RunContextWrapper, WebSearchTool, handoff

from app.agent.agents.fund_manager.sub_agents.sub_agents import SubAgents
from app.agent.models.models import TokenDataFetchInput, WorkflowContext
from app.config.agent_lore import (
    FUND_MANAGER_INSTRUCTIONS,
    FUND_MANAGER_NAME,
    MODEL,
)

# TODO: Major market charts, like fear and greed index
# TODO: Risk agent
# TODO: User personna agent
# TODO: Trading strategy agent
# TODO: Backtesting agent


class FundManager:

    @staticmethod
    def agent() -> Agent:
        sub_agents = SubAgents()
        data_access_tool = sub_agents.data_access_agent().as_tool(
            tool_name="market_data_access_tool",
            tool_description="A tool to fetch price, metadata and sentiment data for any tradeable asset",
        )
        # trade_strategist_agent = sub_agents.technical_strategist_agent().as_tool(
        #     tool_name="trade_strategy_development_tool",
        #     tool_description="An agent that fetches ohlcv data and calculates varios technical indicators from it to generate a trade strategy",
        # )
        try:
            return Agent(
                name=FUND_MANAGER_NAME,
                instructions=FUND_MANAGER_INSTRUCTIONS,
                tools=[data_access_tool],
                model=MODEL,
            )
        except Exception as e:
            raise e

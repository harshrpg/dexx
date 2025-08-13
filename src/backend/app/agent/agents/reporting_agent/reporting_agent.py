from agents import Agent, ModelSettings, WebSearchTool

from app.config.agent_lore import (
    MODEL,
    REPORTING_AGENT_INSTRUCTIONS,
    REPORTING_AGENT_NAME,
)


class ReportingAgent:

    @staticmethod
    def agent():
        return Agent(
            name=REPORTING_AGENT_NAME,
            instructions=REPORTING_AGENT_INSTRUCTIONS,
            model=MODEL,
        )

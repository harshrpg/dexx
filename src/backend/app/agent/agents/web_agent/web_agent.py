from agents import Agent, AgentOutputSchema, ModelSettings, WebSearchTool

from app.agent.models.models import WebAgentResponse
from app.config.agent_lore import MODEL, WEB_SEARCH_AGENT_INSTRUCTIONS


class WebAgent:

    @staticmethod
    def agent() -> Agent:
        return Agent(
            name="DEXX_WEB_SEARCH",
            instructions=WEB_SEARCH_AGENT_INSTRUCTIONS,
            model=MODEL,
            tools=[WebSearchTool()],
            output_type=AgentOutputSchema(WebAgentResponse, strict_json_schema=False),
            model_settings=ModelSettings(
                tool_choice="required",
                temperature=0.7,
            ),
        )

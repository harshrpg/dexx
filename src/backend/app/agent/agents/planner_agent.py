from agents import Agent, ModelSettings, WebSearchTool
from app.agent.models.models import TokenResearchPlan
from app.config.agent_lore import PLANNER_AGENT_NAME, PLANNER_AGENT_INSTRUCTIONS, MODEL

planner_agent = Agent(
    name=PLANNER_AGENT_NAME,
    instructions=PLANNER_AGENT_INSTRUCTIONS,
    model=MODEL,
    # handoffs=[],  # Empty list as we don't need handoffs for the planner
    output_type=TokenResearchPlan,  # Planner outputs a string plan
    tools=[WebSearchTool()],
    model_settings=ModelSettings(tool_choice="required"),
    # mcp_servers=[],
    # mcp_config={},
    # input_guardrails=[],
    # output_guardrails=[],
    # hooks=None,
    # tool_use_behavior="run_llm_again",
    # reset_tool_choice=True,
)

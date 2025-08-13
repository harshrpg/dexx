from typing import List
from agents import Agent, ModelResponse, RunResult, Runner
from dotenv import load_dotenv

from app.config.agent_lore import AGENT_NAME, MODEL, SYSTEM_PROMPT
from app.models.agent_response import AgentResponse


class TradingAssistantAgent:
    def __init__(self):
        load_dotenv()
        self.agent = Agent(name=AGENT_NAME, instructions=SYSTEM_PROMPT)

    async def query_agent(self, prompt: str):
        run_result: RunResult = await Runner.run(self.agent, prompt)
        raw_response: ModelResponse = run_result.raw_responses
        result_list = run_result.to_input_list()
        print(result_list)
        return run_result

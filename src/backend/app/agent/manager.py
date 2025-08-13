import dataclasses
from typing import Any, Optional
import asyncio
from agents import RunResult, Runner, gen_trace_id, trace
from app.agent.agents.fund_manager.fund_manager import FundManager
from app.agent.agents.planner_agent import planner_agent
from app.agent.agents.reporting_agent.reporting_agent import ReportingAgent
from app.agent.agents.web_agent.web_agent import WebAgent
from app.agent.models.models import (
    DexxResponse,
    TokenResearchPlan,
    WebAgentResponse,
    WorkflowContext,
)
from app.core.singleton import Singleton
from app.models.prompt_analysis import TechincalResponse, TokenResponse
from app.models.thread import ChatThread
from app.models.user import User
from app.services.message_service import MessageService
from app.services.data_access.data_access_service import DataAccessService

from rich.console import Console

from app.services.user_service import UserService


class AgentManager(metaclass=Singleton):
    def __init__(self):
        self.console = Console()
        self.message_service = MessageService()
        self.user_service = UserService()
        self.data_access_service = DataAccessService()

    async def __fetch_metadata(
        self, asset_symbol: str, asset_name: str
    ) -> Optional[TokenResponse]:
        """Fetch metadata for a given token symbol."""
        try:
            metadata = self.data_access_service.fetch_metadata(
                token_symbol=asset_symbol, token_query=asset_name
            )
            print("Metadata fetched successfully")
            return metadata
        except Exception as e:
            print(f"Error fetching metadata: {str(e)}")
            return None

    async def run(
        self, query: str, wallet_address: str, thread_id: str, session_id: str
    ) -> DexxResponse:
        """Run the agent pipeline for a given query."""
        result = None
        workflow_context = WorkflowContext(query=query, asset_symbol=None, data=None)

        # Fix: await the async calls
        user, thread_id = await self.user_service.handle_user_prompt(
            wallet_address=wallet_address,
            prompt=query,
            thread_id=thread_id,
            session_id=session_id,
        )
        chat_thread: ChatThread = await self.user_service.get_user_thread(
            wallet_address=wallet_address, thread_id=thread_id
        )
        last_response_id = chat_thread.last_response_id if chat_thread else None

        try:
            trace_id = gen_trace_id()
            with trace(f"Agent_Dexx_workflow_{wallet_address}", trace_id=trace_id):
                # Print status updates
                print("Starting financial research...")
                print(
                    f"View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}"
                )
                print("Planning research...")
                print("Running analysis...")

                # Plan the research
                research_plan = await self.__plan_research(
                    query=query,
                    context=workflow_context,
                    last_response_id=last_response_id,
                )

                # Run metadata fetching and web report generation in parallel
                if research_plan.asset_symbol or research_plan.asset_name:
                    metadata_task = asyncio.create_task(
                        self.__fetch_metadata(
                            research_plan.asset_symbol, research_plan.asset_name
                        )
                    )
                    web_report_task = asyncio.create_task(
                        self.__generate_web_report(
                            context=workflow_context,
                            plan=research_plan,
                            last_response_id=last_response_id,
                        )
                    )

                    # Wait for both tasks to complete
                    metadata, report_result = await asyncio.gather(
                        metadata_task, web_report_task
                    )

                    # Update workflow context with metadata
                    if metadata:
                        technicalResponse = TechincalResponse(
                            metadata=metadata, sentiment=None, strategy=None
                        )
                        workflow_context.data = technicalResponse.model_dump()
                else:
                    # If no token symbol, just generate web report
                    report_result = await self.__generate_web_report(
                        context=workflow_context,
                        plan=research_plan,
                        last_response_id=last_response_id,
                    )

                print(report_result.final_output)
                webAgentResponse = report_result.final_output_as(WebAgentResponse)
                # Fix: await the async call
                await self.user_service.update_thread_response(
                    wallet_address=wallet_address,
                    thread_id=thread_id,
                    response_id=report_result.last_response_id,
                )
                result = DexxResponse(
                    query=query,
                    metadata=(
                        workflow_context.data.get("metadata")
                        if workflow_context.data
                        else None
                    ),
                    insight=webAgentResponse.model_dump(),
                    thread_id=thread_id,
                )

                await self.user_service.add_message_to_thread(
                    wallet_address=wallet_address,
                    thread_id=thread_id,
                    role="assistant",
                    content=result.model_dump(),
                )
            return result

        except Exception as e:
            raise e

    async def __plan_research(
        self,
        query: str,
        context: WorkflowContext,
        last_response_id: str,
    ) -> TokenResearchPlan:
        """Plan the research for a given query."""
        try:
            if last_response_id:
                result = await Runner.run(
                    planner_agent,
                    f"Query: {query}",
                    context=context,
                    previous_response_id=last_response_id,
                )
            else:
                result = await Runner.run(
                    planner_agent, f"Query: {query}", context=context
                )
            print(f"Research plan created: {result.final_output}")
            return result.final_output
        except Exception as e:
            raise e

    async def __run_analysis(
        self, plan: TokenResearchPlan, context: WorkflowContext
    ) -> None:
        try:
            result = await Runner.run(
                FundManager.agent(), f"Plan: {plan}", context=context
            )
            print("Analysis completed successfully")
            return result.final_output
        except Exception as e:
            raise e

    async def __generate_report(
        self, context: WorkflowContext, last_response_id: str
    ) -> RunResult:
        try:
            if last_response_id:
                result = await Runner.run(
                    starting_agent=ReportingAgent.agent(),
                    input=f"fundamental_data: {context.data.metadata.data}, ohlcv: {context.data.strategy.get('ohlcv')}, technical_indicators: {context.data.strategy.get('indicators')}",
                    context=context,
                    previous_response_id=last_response_id,
                )
            else:
                result = await Runner.run(
                    starting_agent=ReportingAgent.agent(),
                    input=f"fundamental_data: {context.data.metadata.data}, ohlcv: {context.data.strategy.get('ohlcv')}, technical_indicators: {context.data.strategy.get('indicators')}",
                    context=context,
                )
            print("Report generated")
            return result
        except Exception as e:
            raise e

    async def __generate_web_report(
        self, context: WorkflowContext, plan: TokenResearchPlan, last_response_id: str
    ) -> RunResult:
        try:
            if last_response_id:
                result = await Runner.run(
                    WebAgent.agent(),
                    f"User query: {context.query}, Research Plan: {plan}",
                    context=context,
                    previous_response_id=last_response_id,
                )
            else:
                result = await Runner.run(
                    WebAgent.agent(),
                    f"Research Plan: {plan}",
                    context=context,
                )
            print("Web Report generated")
            return result
        except Exception as e:
            raise e

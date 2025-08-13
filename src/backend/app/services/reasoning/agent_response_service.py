import json
import logging
import os
from typing import Dict, List
from dotenv import load_dotenv

from app.api.client.openai.openai_api_client import OpenAiAPIClient
from openai.types.responses import Response
from app.services.data_access.data_access_service import DataAccessService
from app.services.processing.data_processing_service import DataProcessingService
from app.services.technical_analysis.technical_analysis_service import TechnicalAnalysisService
from app.services.reasoning.constants import ASSETS, FUNCTION_CALL_TYPE
from app.services.reasoning.tools_service import ToolsService
load_dotenv()

class AgentResponseService:
    def __init__(self):
        self.client = OpenAiAPIClient(os.getenv("OPENAI_API_KEY"))
        self.dal = DataAccessService()
        self.dps = DataProcessingService()
        self.technical_analysis_service = TechnicalAnalysisService()
        self.tools_service = ToolsService()
        self.logger = logging.getLogger(__name__)
    
    def respond(self, messages: List):
        tool_response = self.client.generate_tool_response(messages=messages)
        return self.process_tools(tool_response, messages)

    def process_tools(self, tool_response: Response, messages: List):
        result = None
        final_response = None
        for response_output_item in tool_response.output:
            result = self.tools_service.process_tools(response_output_item, messages)
        final_response = self.client.generate_response(messages)
        return final_response, messages, result
                

    

import json
import logging
from typing import List
from app.services.processing.data_processing_service import DataProcessingService
from app.services.reasoning.constants import ASSETS, FUNCTION_CALL_TYPE, MESSAGE, WEB_SEARCH_CALL

from openai.types.responses import ResponseOutputItem

class ToolsService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.data_processing_service = DataProcessingService()

    def __get_tools(self):
        return {
                "get_crypto_data_market_indicators_sentiments": self.get_crypto_data_market_indicators_sentiments,
                "fetch_latest_tokens": self.get_latest_tokens
            }
    
    def process_tools(self, tool_response_output_item: ResponseOutputItem, messages: List):
        result = None
        if tool_response_output_item.type == FUNCTION_CALL_TYPE:
            tool_method = self.__get_tools()[tool_response_output_item.name]
            try:    
                arguments = json.loads(tool_response_output_item.arguments)
                if not arguments or ASSETS not in arguments:
                    result = tool_method()
                else:
                    result = tool_method(arguments[ASSETS])
                messages.append(tool_response_output_item)
                messages.append({           
                    "type": "function_call_output",
                    "call_id": tool_response_output_item.call_id,
                    "output": json.dumps(result)
                })
            except Exception as e:
                self.logger.error(f"Error processing tool {tool_response_output_item.name}: {e}")
                return None
        elif tool_response_output_item.type == MESSAGE:
            messages.append({
                "role": 'assistant',
                "content": tool_response_output_item.content[0].text
            })
            # result = tool_response_output_item.content[0].text
        return result
    
    def get_latest_tokens(self):
        return self.data_processing_service.fetch_latest_tokens()

    def get_crypto_data_market_indicators_sentiments(self, assets: List):
        """Fetch crypto data and market indicators."""
       
        default_response = {
            "token_metadata": "Not Available",
            "market_indicators": "Not Available",
            "sentiments": "Not Available"
        }

        if len(assets) == 0:
            return default_response

        def get_single_token_data(asset):
            try:
                return {
                    "asset": asset,
                    "data": self.data_processing_service.fetch_token_data_and_process(token_symbol=asset)
                }
            except Exception as e:
                self.logger.error(f"Error fetching data for {asset}: {e}")
                return {"asset": asset, "data": default_response}

        return [get_single_token_data(asset) for asset in assets]
from app.models.prompt_analysis import ProcessedPrompt, PromptAnalysis
import logging

from app.services.data_access.data_access_service import DataAccessService


class PromptProcessingServiceV2:

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.dal_service = DataAccessService()

    def process(self, prompt_analysis: PromptAnalysis) -> ProcessedPrompt:
        if prompt_analysis.token_name:
            token_query = prompt_analysis.token_name
        elif prompt_analysis.token_symbol:
            token_query = prompt_analysis.token_symbol
        else:
            token_query = None
        metadata = self.dal_service.fetch_metadata(
            token_query=token_query,
            contract_address=prompt_analysis.contract_address,
            chain=prompt_analysis.chain,
            token_symbol=prompt_analysis.token_symbol,
        )
        processed_prompt = ProcessedPrompt(
            prompt_analysis=prompt_analysis,
            metadata=metadata,
            actions=prompt_analysis.actions,
        )
        return processed_prompt

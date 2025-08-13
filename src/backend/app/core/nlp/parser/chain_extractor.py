from app.models.chains import ChainMapping


class ChainExtractor:
    def __init__(self, chain_mapping: ChainMapping):
        self.chain_mapping = chain_mapping

    def extract_chain(self, prompt: str, nlp_doc) -> str:
        prompt_lower = prompt.lower()
        chain_data = self.chain_mapping.root

        # Direct chain name match
        for chain_id, chain_info in chain_data.items():
            if any(name in prompt_lower for name in chain_info.names):
                return chain_id

        # Context-based chain detection
        chain_context_words = {"chain", "network", "blockchain", "on", "in"}
        for token in nlp_doc:
            if token.text in chain_context_words:
                nearby_tokens = list(token.children) + [token.head]
                for nearby in nearby_tokens:
                    for chain_id, chain_info in chain_data.items():
                        if nearby.text in chain_info.names:
                            return chain_id

        # Default chain
        for chain_id, chain_info in chain_data.items():
            if chain_info.default:
                return chain_id

        return "eth"

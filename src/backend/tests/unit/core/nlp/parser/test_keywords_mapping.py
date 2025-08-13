from app.core.nlp.parser.keyword_mappings import KeywordMappings
from app.models.chains import ChainMapping, ChainDetails  # Import the models


class TestKeywordMapping:

    def test_chain_mapping_loads_correctly(self):
        mapping = KeywordMappings()
        chain_map = mapping.chain_mappings
        assert isinstance(
            chain_map, ChainMapping
        ), "Should return a ChainMapping instance"
        chain_data = chain_map.root
        assert isinstance(chain_data, dict), "Chain mapping should be a dictionary"
        essential_chains = {"eth", "bsc", "polygon", "avalanche", "arbitrum", "base"}
        assert all(
            chain in chain_data for chain in essential_chains
        ), "Missing essential chains"
        eth_data = chain_data["eth"]
        assert isinstance(eth_data, ChainDetails), "Should be a ChainDetails instance"
        assert isinstance(eth_data.names, set), "Names should be a set"
        assert isinstance(eth_data.default, bool), "Default should be a boolean"
        assert eth_data.default is True, "Ethereum should be the default chain"
        expected_eth_names = {"ethereum", "eth", "mainnet", "ether"}
        assert expected_eth_names.issubset(
            eth_data.names
        ), "Missing expected ethereum names"
        default_chains = [
            chain for chain, details in chain_data.items() if details.default
        ]
        assert len(default_chains) == 1, "Should have exactly one default chain"
        assert default_chains[0] == "eth", "Ethereum should be the only default chain"

class ChainTestPrompts:
    DIRECT_CHAIN_MENTIONS = {
        "eth": [
            "Show me token info on ethereum",
            "What's the price on eth",
            "Get holders on mainnet",
            "Check ether transactions",
        ],
        "bsc": [
            "Show BSC token holders",
            "What's happening on Binance Smart Chain",
            "Get BNB chain statistics",
            "Check binance transactions",
        ],
        "polygon": [
            "Show me MATIC stats",
            "What's trending on Polygon",
            "Get polygon holders",
            "Check matic network activity",
        ],
        "arbitrum": [
            "Show me ARB tokens",
            "What's hot on Arbitrum",
            "Get arbitrum one statistics",
            "Check arbitrum nova activity",
        ],
    }

    CONTEXTUAL_CHAIN_MENTIONS = {
        "eth": [
            "Show me tokens on the ethereum network",
            "What's happening in the eth blockchain",
            "Get stats for chain ethereum",
            "Check activity in mainnet network",
        ],
        "bsc": [
            "Show tokens on the BSC network",
            "What's trending in binance chain",
            "Get info for blockchain BSC",
            "Check activity in BNB network",
        ],
    }

    AMBIGUOUS_PROMPTS = [
        "Show me token information",
        "What's the latest price",
        "Get holder statistics",
        "Check transaction activity",
        "Show me the market data",
    ]

    COMPLEX_PROMPTS = {
        "eth": [
            "In the ethereum blockchain, show me the top holders",
            "Looking at eth network, what's the price trend",
            "Within mainnet ecosystem, get token stats",
        ],
        "polygon": [
            "For the polygon network, show holder distribution",
            "In matic chain, what's the volume like",
            "On the polygon blockchain, get transaction count",
        ],
    }

    MULTIPLE_CHAIN_MENTIONS = {
        "first_mentioned": {
            ("eth", "bsc"): [
                "Compare ethereum and bsc prices",
                "Show holders on eth vs binance",
                "Get stats for mainnet and bnb",
            ],
            ("polygon", "arbitrum"): [
                "Compare matic and arbitrum activity",
                "Show holders on polygon vs arb",
                "Get stats for matic and arbitrum one",
            ],
        }
    }

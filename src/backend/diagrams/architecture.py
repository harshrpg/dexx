from diagrams import Diagram, Cluster
from diagrams.programming.framework import FastAPI
from diagrams.programming.language import Python
from diagrams.onprem.client import Client
from diagrams.onprem.inmemory import Redis
from diagrams.saas.chat import Discord
from diagrams.onprem.network import Internet
from diagrams.aws.security import IAM
from diagrams.aws.storage import SimpleStorageServiceS3

# Original Architecture
with Diagram("Original Web3 Analysis Architecture", show=False, direction="TB"):
    client = Client("User")

    with Cluster("FastAPI Server"):
        api = FastAPI("FastAPI")

        with Cluster("Core Services"):
            prompt_parser = Python("Prompt Parser")
            endpoint_service = Python("Endpoint Service")
            insight_service = Python("Insight Service")

        with Cluster("Token Services"):
            token_client = Python("Token Client")
            wallet_client = Python("Wallet Client")

    with Cluster("External Services"):
        moralis = Internet("Moralis API")
        chatgpt = Discord("ChatGPT API")

    # Define the flow
    client >> api >> prompt_parser
    prompt_parser >> token_client
    prompt_parser >> wallet_client
    token_client >> endpoint_service
    wallet_client >> endpoint_service
    endpoint_service >> moralis
    moralis >> insight_service
    insight_service >> chatgpt

# Updated Multi-user Architecture
with Diagram(
    "Updated Multi-user Web3 Analysis Architecture", show=False, direction="TB"
):
    client = Client("Multiple Users")

    with Cluster("Authentication Layer"):
        auth = IAM("Auth Service")
        rate_limiter = Python("Rate Limiter")

    with Cluster("Storage Layer"):
        cache = Redis("Redis Cache")
        user_store = SimpleStorageServiceS3("User Store")

    with Cluster("FastAPI Server"):
        api = FastAPI("FastAPI")

        with Cluster("Core Services"):
            prompt_parser = Python("Prompt Parser")
            endpoint_service = Python("Endpoint Service")
            insight_service = Python("Insight Service")

        with Cluster("Token Services"):
            token_client = Python("Token Client")
            wallet_client = Python("Wallet Client")

        with Cluster("User Services"):
            user_prefs = Python("User Preferences")
            session_mgr = Python("Session Manager")

    with Cluster("External Services"):
        moralis = Internet("Moralis API")
        chatgpt = Discord("ChatGPT API")

    # Define the updated flow
    client >> auth
    auth >> rate_limiter
    rate_limiter >> api

    api >> prompt_parser
    prompt_parser >> token_client
    prompt_parser >> wallet_client

    token_client >> endpoint_service
    wallet_client >> endpoint_service

    endpoint_service >> cache
    cache >> moralis
    moralis >> insight_service
    insight_service >> chatgpt

    # User management flow
    api >> user_prefs
    user_prefs >> user_store
    api >> session_mgr
    session_mgr >> cache

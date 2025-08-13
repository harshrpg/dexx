class ApiClient:
    def __init__(self, api_key: str):
        self.api_key = api_key

    def print_api_key(self) -> str:
        print(f"API Key::{self.api_key}")
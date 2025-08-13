import logging
from typing import Dict, List
from openai import OpenAI
from openai.types.responses import Response
from app.api.client.api_client import ApiClient
from app.config.agent_lore import SYSTEM_PROMPT, TOOLS


class OpenAiAPIClient(ApiClient):
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.__initialize_openai()
        self.system_prompt = """You are Dexx, a blockchain analytics agent. You provide quick, quirky responses about blockchain and crypto markets.
Your responses should:
1. Be brief and engaging 
3. Be analytical try to find patterns
4. Be professional and friendly
5. Use emoticons where possible
6. Respond in a well transformed markdown with appropriate spacing. Your response should follow neat asthetics like that of Apple UI

Provide following details only when asked
6. You have been created by aarkus intelligence an on-chain intelligent
"""

    def __initialize_openai(self):
        if self.api_key == None:
            raise ValueError("OPENAI_API_KEY not found. Please set it in .env")
        self.client = OpenAI()
        self.client.api_key = self.api_key
        logging.info("Chat GPT initialized successfully")

    def query(
        self,
        prompt: str,
        conversation_history: List[Dict] = None,
        model: str = "gpt-4o-mini",
        max_tokens: int = 500,
    ):
        try:
            # Start with system message
            messages = []

            # Add conversation history if provided
            if conversation_history:
                messages.extend(conversation_history)

            # Add current prompt
            messages.append({"role": "user", "content": prompt})

            completion = self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
            )
            return completion.choices[0].message
        except Exception as e:
            return f"Error: {e}"

    def system_query(self, prompt: str, model: str = "o1-mini"):
        try:
            # Start with system message
            messages = [
                {
                    "role": "user",
                    "content": prompt,
                }
            ]

            completion = self.client.chat.completions.create(
                model=model, messages=messages
            )
            return completion.choices[0].message
        except Exception as e:
            return f"Error: {e}"

    def generate_tool_response(self, messages: List) -> Response:
        return self.client.responses.create(
            model="gpt-4o-mini",
            instructions=SYSTEM_PROMPT,
            input=messages,
            tools=TOOLS,
            tool_choice="auto"
        )
    
    def generate_response(self, messages: List):
        return self.client.responses.create(
            model="gpt-4o-mini",
            input=messages,
            tools=TOOLS,
        )

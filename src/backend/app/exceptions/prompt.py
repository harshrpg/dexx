from fastapi import HTTPException


class PromptError(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=400, detail=detail)


class EmptyPromptError(PromptError):
    def __init__(self):
        super().__init__("Prompt cannot be empty")


class RateLimitExceeded(HTTPException):
    def __init__(self):
        super().__init__(status_code=429, detail="Rate limit exceeded")


class ValidationError(PromptError):
    pass

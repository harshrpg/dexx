from typing import Dict, Set
from pydantic import BaseModel, RootModel


class ChainDetails(BaseModel):
    names: Set[str]
    default: bool


class ChainMapping(RootModel[Dict[str, ChainDetails]]):
    pass

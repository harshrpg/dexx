from typing import List
from pydantic import BaseModel


class CryptocurrencySymbol_Mobula(BaseModel):
    id: int
    name: str
    symbol: str


class GetAllCryptocurrencies_Mobula_Data(BaseModel):
    data: List[CryptocurrencySymbol_Mobula]

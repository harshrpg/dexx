from dotenv import load_dotenv
import os
import numpy as np
import pandas as pd
from typing import Dict
from openai import OpenAI
import time
import json
import requests


load_dotenv()

client = OpenAI()
client.api_key = os.getenv("OPENAI_API_KEY")

CRYPTOPANIC_API_KEY = os.getenv("CRYPTOPANIC_API_KEY")
ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY")

MOBULA_TOKEN_METADATA_API_URL = os.getenv(
    "MOBULA_TOKEN_METADATA_API_URL", "https://production-api.mobula.io/api/1/metadata"
)

MOBULE_LATEST_TOKENS_API_URL = os.getenv(
    "MOBULE_LATEST_TOKENS_API_URL",
    "https://production-api.mobula.io/api/1/market/query/token"
)

MOBULA_PRICE_HISTORY_API_URL = os.getenv(
    "MOBULA_PRICE_HISTORY_API_URL",
    "https://production-api.mobula.io/api/1/market/history",
)

MOBULA_OHLCV_HISTORY_API_URL = os.getenv(
    "MOBULA_OHLCV_HISTORY_API_URL",
    "https://production-api.mobula.io/api/1/market/history/pair",
)

# def get_weather(latitude, longitude, units, location):
#     response = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,wind_speed_10m&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m")
#     data = response.json()
#     return f"The current temperature in {location} is {data['current']['temperature_2m']} degree {units}."

def get_sentiment_analysis_data(token_symbol):
    """Fetch sentiment analysis data from CryptoPanic API"""
    url = f"https://cryptopanic.com/api/free/v1/posts/?auth_token={CRYPTOPANIC_API_KEY}&currencies={token_symbol}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        # print(data["results"])
        return data["results"]
    else:
        return None

def analyze_sentiment(news_items):
    """
    Analyze sentiment from news items.
    
    Args:
        news_items: List of news items from CryptoPanic API
        
    Returns:
        Dictionary containing sentiment analysis
    """
    # print(f"News Items: {news_items}")

    if not news_items:
        return {
            "overall": "neutral",
            "score": 0,
            "bullish_count": 0,
            "bearish_count": 0,
            "neutral_count": 0
        }
        
    sentiment_counts = {
        "bullish": 0,
        "bearish": 0,
        "neutral": 0
    }
    
    for item in news_items:
        votes = item.get("votes", {})
        # Count sentiment based on votes
        if votes.get("positive", 0) > votes.get("negative", 0):
            sentiment_counts["bullish"] += 1
        elif votes.get("negative", 0) > votes.get("positive", 0):
            sentiment_counts["bearish"] += 1
        else:
            sentiment_counts["neutral"] += 1
            
    total_items = len(news_items)
    sentiment_score = (
        (sentiment_counts["bullish"] - sentiment_counts["bearish"]) / 
        total_items if total_items > 0 else 0
    )
    
    # Determine overall sentiment
    if sentiment_score > 0.2:
        overall = "bullish"
    elif sentiment_score < -0.2:
        overall = "bearish"
    else:
        overall = "neutral"
        
    return {
        "overall": overall,
        "score": sentiment_score,
        "bullish_count": sentiment_counts["bullish"],
        "bearish_count": sentiment_counts["bearish"],
        "neutral_count": sentiment_counts["neutral"]
    } 


def fetch_token_metadata(token_symbol):
    """Fetch token metadata from Mobula API"""
    url = f"{MOBULA_TOKEN_METADATA_API_URL}?asset={token_symbol}"
    try:
        response = requests.get(url)
        token_metadata = response.json()
        # print(token_metadata['data']['blockchains'])

        return token_metadata
    except Exception as e:
        print(f"Error fetching token metadata: {e}")
        return None
        

def get_ohlcv_data(token_symbol, blockchain, days=7):
    
    # Timestamps conversion in milliseconds
    current_timestamp = int(time.time() * 1000)
    days_ago_timestamp = int((time.time() - days * 24 * 60 * 60) * 1000)
    
    """ Fetch historical prices from Mobula API """
    try:
        url = f"{MOBULA_OHLCV_HISTORY_API_URL}?symbol={token_symbol}&blockchain={blockchain}&from={days_ago_timestamp}&to={current_timestamp}&period=1h"

        response = requests.get(url)
        ohlcv_data = response.json()

        ohlcv_data["blockchain"] = blockchain
        ohlcv_data["asset"] = token_symbol

        print(f"OHLCV DATA: {ohlcv_data}")

        if ohlcv_data.get("data") is None:
            print(f"Error fetching OHLCV data from data['error'] block: {ohlcv_data["error"]}")
            return  {
                "blockchain": blockchain,
                "asset": token_symbol,
                "data": []
            }
        
        return ohlcv_data
    
    except Exception as e:
        print(f"Error fetching OHLCV data - from exception block: {e}")
        return {
            "blockchain": blockchain,
            "asset": token_symbol,
            "data": []
        }

def calculate_indicators(ohlcv_data):
    """Calculate technical indicators from OHLCV data.
    
    Args:
        ohlcv_data: List of dictionaries containing OHLCV data
        
    Returns:
        Dictionary containing calculated indicators
    """
    try:
        # print(f"OHLCV Data in Calculate Indicators: {ohlcv_data.get("data")}")

        if len(ohlcv_data.get("data")) == 0:
            print(f"No OHLCV data found for {ohlcv_data.get('asset')} on {ohlcv_data.get('blockchain')}")
            return f"No OHLCV data found for {ohlcv_data.get('asset')} on {ohlcv_data.get('blockchain')}"
        
        # Convert to pandas DataFrame
        df = pd.DataFrame(ohlcv_data["data"])
        df["blockchain"] = ohlcv_data["blockchain"]
        df["asset"] = ohlcv_data["asset"]

        # Convert milliseconds to datetime
        df['time'] = pd.to_datetime(df['time'], unit='ms')
        df.set_index('time', inplace=True)
        
        # Calculate indicators
        indicators = {
            'asset': df['asset'].iloc[-1],
            'blockchain': df['blockchain'].iloc[-1],
            'trend': _calculate_trend(df),
            'rsi': _calculate_rsi(df),
            'macd': _calculate_macd(df),
            'bollinger_bands': _calculate_bollinger_bands(df),
            'moving_averages': _calculate_moving_averages(df),
            'support_resistance': _calculate_support_resistance(df)
        }
        
        return indicators
        
    except Exception as e:
        print(f"Error calculating indicators: {e}")
        return f"No Technical Indicators data found for {ohlcv_data.get('asset')} on {ohlcv_data.get('blockchain')}"

def _calculate_trend(df: pd.DataFrame) -> Dict:
    """Calculate trend using multiple timeframes."""
    try:
        # Calculate 20, 50, and 200-day moving averages
        ma20 = df['close'].rolling(window=20).mean()
        ma50 = df['close'].rolling(window=50).mean()
        ma200 = df['close'].rolling(window=200).mean()
        
        current_price = df['close'].iloc[-1]
        
        trend = {
            'direction': 'bullish' if current_price > ma20.iloc[-1] > ma50.iloc[-1] > ma200.iloc[-1] else 'bearish',
            'strength': 'strong' if abs(current_price - ma20.iloc[-1]) / ma20.iloc[-1] > 0.02 else 'weak',
            'ma20': ma20.iloc[-1],
            'ma50': ma50.iloc[-1],
            'ma200': ma200.iloc[-1]
        }
        
        return trend
        
    except Exception as e:
        print(f"Error calculating trend: {e}")
        return "No Technical Indicators found"

def _calculate_rsi(df: pd.DataFrame, period: int = 14) -> Dict:
    """Calculate Relative Strength Index using Wilder's smoothing method (matching TradingView)."""
    try:
        # Calculate price changes
        delta = df['close'].diff()
        
        # Calculate gains and losses
        gains = delta.where(delta > 0, 0)
        losses = -delta.where(delta < 0, 0)

            # Create result Series initialized with NaNs
        rsi = pd.Series(index=df.index)
        
        # We need at least period+1 data points to calculate first RSI value
        if len(df) <= period:
            return {
                'value': np.nan,
                'signal': 'neutral',
                'trend': 'neutral'
            }
        
        # First average (SMA for initial period)
        first_avg_gain = gains.iloc[:period].mean()
        first_avg_loss = losses.iloc[:period].mean()

        if first_avg_loss == 0:
            rsi.iloc[period] = 100
        else:
            rs = first_avg_gain / first_avg_loss
            rsi.iloc[period] = 100 - (100 / (1 + rs))
        
        # Calculate RSI using Wilder's smoothing method
        avg_gain = first_avg_gain
        avg_loss = first_avg_loss
        
        # Initialize smoothed averages list with first values
        smoothed_gains = [first_avg_gain]
        smoothed_losses = [first_avg_loss]
        
        # Calculate subsequent averages using Wilder's smoothing (α = 1/period)
        # Formula: avg_gain = (previous_avg_gain * (period - 1) + current_gain) / period
        for idx in range(period + 1, len(df)):
            current_gain = gains.iloc[idx]
            current_loss = losses.iloc[idx]
            
            # Apply Wilder's smoothing formula
            avg_gain = ((avg_gain * (period - 1)) + current_gain) / period
            avg_loss = ((avg_loss * (period - 1)) + current_loss) / period
            
            # Calculate RSI
            if avg_loss == 0:
                rsi.iloc[idx] = 100
            else:
                rs = avg_gain / avg_loss
                rsi.iloc[idx] = 100 - (100 / (1 + rs))
    
        current_rsi = rsi.iloc[-1]
        
        return {
            'value': current_rsi,
            'signal': 'overbought' if current_rsi > 70 else 'oversold' if current_rsi < 30 else 'neutral',
            'trend': 'bullish' if current_rsi > 50 else 'bearish'
        }
        
    except Exception as e:
        print(f"Error calculating RSI: {e}")
        return "No Technical Indicators found"

def _calculate_macd(df: pd.DataFrame) -> Dict:
    """Calculate MACD (Moving Average Convergence Divergence).
    Fast length: 12
    Slow length: 26
    Signal length: 9
    Source: Close price
    """
    try:
        # Calculate EMAs
        fast_ema = df['close'].ewm(span=12, adjust=False, min_periods=12).mean()
        slow_ema = df['close'].ewm(span=26, adjust=False, min_periods=26).mean()
        
        # Calculate MACD line
        macd_line = fast_ema - slow_ema
        
        # Calculate Signal line with 9-period EMA of MACD
        signal_line = macd_line.ewm(span=9, adjust=False, min_periods=9).mean()
        
        # Calculate histogram
        histogram = macd_line - signal_line
        
        # Get latest values
        current_macd = macd_line.iloc[-1]
        current_signal = signal_line.iloc[-1]
        current_hist = histogram.iloc[-1]
        
        # Determine trend and crossover
        trend = 'bullish' if current_macd > current_signal else 'bearish'
        
        # Check for crossover in last 2 periods
        crossover = 'none'
        if len(histogram) >= 2:
            if histogram.iloc[-2] < 0 and histogram.iloc[-1] > 0:
                crossover = 'bullish'
            elif histogram.iloc[-2] > 0 and histogram.iloc[-1] < 0:
                crossover = 'bearish'
        
        return {
            'macd': current_macd,
            'signal': current_signal,
            'histogram': current_hist,
            'trend': trend,
            'crossover': crossover
        }
        
    except Exception as e:
        print(f"Error calculating MACD: {e}")
        return "No Technical Indicators found"

def _calculate_bollinger_bands(df: pd.DataFrame, period: int = 20, std_dev: float = 2.0) -> Dict:
    """Calculate Bollinger Bands."""
    try:
        ma = df['close'].rolling(window=period).mean()
        std = df['close'].rolling(window=period).std()
        
        upper_band = ma + (std * std_dev)
        lower_band = ma - (std * std_dev)
        
        current_price = df['close'].iloc[-1]
        
        return {
            'upper': upper_band.iloc[-1],
            'middle': ma.iloc[-1],
            'lower': lower_band.iloc[-1],
            'bandwidth': (upper_band.iloc[-1] - lower_band.iloc[-1]) / ma.iloc[-1],
            'position': 'upper' if current_price > upper_band.iloc[-1] else 'lower' if current_price < lower_band.iloc[-1] else 'middle'
        }
        
    except Exception as e:
        print(f"Error calculating Bollinger Bands: {e}")
        return "No Technical Indicators found"

def _calculate_moving_averages(df: pd.DataFrame) -> Dict:
    """Calculate various moving averages."""
    try:
        periods = [20, 50, 200]
        mas = {}
        
        for period in periods:
            mas[f'ma{period}'] = df['close'].rolling(window=period).mean().iloc[-1]
        
        return mas
        
    except Exception as e:
        print(f"_calculate_moving_averages: Error: {e}")
        return "No Technical Indicators found"

def _calculate_support_resistance(df: pd.DataFrame, window: int = 20) -> Dict:
    """Calculate support and resistance levels."""
    try:
        recent_data = df.tail(window)
        
        # Find local minima and maxima
        highs = recent_data['high'].values
        lows = recent_data['low'].values
        
        # Simple support/resistance calculation
        resistance = np.max(highs)
        support = np.min(lows)
        
        current_price = df['close'].iloc[-1]
        
        return {
            'support': support,
            'resistance': resistance,
            'distance_to_support': (current_price - support) / current_price,
            'distance_to_resistance': (resistance - current_price) / current_price
        }
        
    except Exception as e:
        print(f"_calculate_support_resistance: Error: {e}")
        return "No Technical Indicators found" 

#fetch latest tokens from https://production-api.mobula.io/api/1/market/query/token?sortBy=listed_at&sortOrder=desc&blockchain=Base
def fetch_latest_tokens(intent):
    if intent:
        url = f"{MOBULE_LATEST_TOKENS_API_URL}?sortBy=listed_at&sortOrder=desc"
        response = requests.get(url)
        return response.json()
    else:
        return None
        
    

def get_crypto_data_market_indicators_sentiments(assets, blockchain=None):
    """Fetch crypto data and market indicators."""

    print(f"Passed Blockchain Param: {blockchain}")
    if len(assets) == 0:
        return {
            "token_metadata": "Not Available",
            "ohlcv_data": "Not Available",
            "market_indicators": "Not Available",
            "sentiments": "Not Available"
        }
    
    if len(assets) > 1:
        all_tokens_data = []
        # TODO - process assets parallely
        for asset in assets:
            print(f"Doing analysis for {asset}")
            try:
                # TODO - process (metadata->ohlcv->indicator) and (sentiments) parallely
                
                metadata = fetch_token_metadata(token_symbol=asset)

                if not blockchain:
                    print(f"Initial Blockchain: {blockchain}")
                    blockchain = metadata['data']['blockchains'][0]
                    print(f"Updated Blockchain : {blockchain}")
                    ohlcv_data = get_ohlcv_data(token_symbol=asset, blockchain=blockchain)
                    indicators = calculate_indicators(ohlcv_data)
                    blockchain = None
                elif blockchain not in metadata['data']['blockchains']:
                    updated_blockchain = metadata['data']['blockchains'][0]
                    print(f"Initial Blockchain: {blockchain} | Updated Blockchain : {updated_blockchain}")
                    ohlcv_data = get_ohlcv_data(token_symbol=asset, blockchain=updated_blockchain)
                    indicators = calculate_indicators(ohlcv_data)
                    # blockchain = None
                else:
                    print(blockchain)
                    ohlcv_data = get_ohlcv_data(token_symbol=asset, blockchain=blockchain)
                    indicators = calculate_indicators(ohlcv_data)

                
                sentiments = analyze_sentiment(get_sentiment_analysis_data(token_symbol=asset))

                all_tokens_data.append({"asset": asset, "data": {"token_metadata": metadata, "ohlcv_data": ohlcv_data, "market_indicators": indicators, "sentiments": sentiments}})
            
            except Exception as e:
                print(f"Error fetching crypto data and market indicators: {e}")
                all_tokens_data.append({"asset": asset, "data": {"token_metadata": "Not Available", "ohlcv_data": "Not Available", "market_indicators": "Not Available", "sentiments": "Not Available"}})
        
        return all_tokens_data
    
    try:
        print(f"Doing analysis for {assets[0]}")
        metadata = fetch_token_metadata(token_symbol=assets[0])

        if not blockchain:
            blockchain = metadata['data']['blockchains'][0]
        elif blockchain not in metadata['data']['blockchains']:
            blockchain = metadata['data']['blockchains'][0]
        else:
            blockchain = blockchain
                
        print(blockchain)

        ohlcv_data = get_ohlcv_data(token_symbol=assets[0], blockchain=blockchain)
        indicators = calculate_indicators(ohlcv_data)
        sentiments = analyze_sentiment(get_sentiment_analysis_data(token_symbol=assets[0]))

        return {
            "token_metadata": metadata,
            "ohlcv_data": ohlcv_data,
            "market_indicators": indicators,
            "sentiments": sentiments
        }
    except Exception as e:
        print(f"Error fetching crypto data and market indicators: {e}")
        return {
            "token_metadata": "Not Available",
            "ohlcv_data": "Not Available",
            "market_indicators": "Not Available",
            "sentiments": "Not Available"
        }


SYSTEM_PROMPT = """
You are Dexx, a blockchain analytics agent. You provide quick, quirky responses about blockchain and crypto markets.

You goal is to provide most appropriate response based on the user query.
- For general queries or news including mention of a crypto coin/token or NFT, use 'web_search_preview' tool to answer the user query as per most recent search results. 
- For user queries around new tokens use 'fetch_latest_tokens' tool for getting the relevant data. 
- For user queries around trading strategy or technical discussion use 'get_crypto_data_market_indicators_sentiments' tool for getting the relevant data. 


You have access to the following tools:
1. Fetch Latest Tokens Onchain: 'fetch_latest_tokens' 
2.Crypto Data & Market Indicators Tools: 'get_crypto_data_market_indicators_sentiments'
3. Web Search Tool: 'web_search_preview'

You can use multiple tools to answer a user query, as required. Do not call a tool again if you already have information about the user query in the current thread.

Do not use any other tools or answer about any other topic unrelated to blockchain or crypto or stock markets. If user query is about any other topic, tell the user You can only answer question related to blockchain or crypto.

Provide a focused analysis in the form of bullet points and tabular format as necessary for easier readabiliy. When providing technical analysis mention the blockchain details as well, if available.

Your responses should:
1. Use emojis as much as possible
2. Be crisp and engaging 
3. Be analytical try to find patterns
4. Be professional and friendly
5. Respond in a well transformed markdown with appropriate spacing. Your response should follow neat asthetics like that of Apple UI.
6. Also, append the current 'asset' for which the query was intended in the final response. Select only one asset such that this asset is the main focus of the conversation. (e.g. Queried Asset: LINK or Chainlink)

Provide following details only when asked:
You have been created by Aarkus Intelligence an on-chain intelligence agent.

"""

tools = [ 
        { 
            "type": "web_search_preview" 
        },
        {
            "type": "function",
                "name": "fetch_latest_tokens",
                "description": "Retrieves Newly Listed Tokens Onchain. A direct way to obtain real-time, detailed information about tokens immediately upon their market introduction.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "new_token_search_intent": {
                            "type": "string",
                            "description": "Intent for new tokens search for analysis. True or False"
                        },
                    },
                    "required": [
                        "new_token_search_intent"
                    ],
                    "additionalProperties": False
                },
        },
        {
            "type": "function",
                "name": "get_crypto_data_market_indicators_sentiments",
                "description": "Retrieves crypto metadata, market indicators and sentiments for the given asset names or symbols on a blockchain. Multiple assets could be separated using commas or backslashes. Use 'Ethereum' as the default blockchain if not provided by user.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "assets": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            }
                        },
                        "blockchain": {
                            "type": "string",
                            "enum": ['Ethereum', 'Solana', 'Polygon', 'BNB Smart Chain (BEP20)', 'Avalanche C-Chain', 'GraphLinq', 'Optimistic',  'Abstract', 'Mantle', 'Linea', 'Berachain', 'Arbitrum', 'Blast', 'Abstract', 'Base', 'Plume', 'Moonriver', 'Vanar Vanguard Testnet', 'Moonbeam', 'Optimistic', 'Alephium', 'Celo', 'Zora', 'Ink', 'Blast', 'Mode', 'XDAI', 'Scroll', 'Polygon zkEVM']
                        },
                    },
                    "required": [
                        "assets"
                    ],
                    "additionalProperties": False
                },
        }
]

# Process Tool Calls
def process_tool_calls(response, input_messages):

    # Return response, input message if no tool calls

    for tool_call in response.output:
        # print(tool_call)
        if tool_call:
            if tool_call.type == 'function_call':
                if tool_call.name == 'get_crypto_data_market_indicators_sentiments':
                    args = json.loads(tool_call.arguments)
                    
                    if 'blockchain' not in args:
                        args['blockchain'] = None
                    
                    print(f"Tool Call Arguments: {args}")

                    result = get_crypto_data_market_indicators_sentiments(args["assets"], args["blockchain"])

                    input_messages.append(tool_call)  # append model's function call message
                    input_messages.append({           # append result message
                        "type": "function_call_output",
                        "call_id": tool_call.call_id,
                        "output": json.dumps(result)
                    })
                elif tool_call.name == 'fetch_latest_tokens':
                    args = json.loads(tool_call.arguments)
                    result = fetch_latest_tokens(args["new_token_search_intent"])

                    input_messages.append(tool_call)  # append model's function call message
                    input_messages.append({           # append result message
                        "type": "function_call_output",
                        "call_id": tool_call.call_id,
                        "output": json.dumps(result)
                    })
        
    final_response = client.responses.create(
        model="gpt-4o-mini",
        input=input_messages,
        tools=tools,
    )

    print(f"Final Response: {final_response.output_text}")

    return final_response, input_messages

from fastapi import FastAPI, Request
from pydantic import BaseModel

app = FastAPI()

class PromptRequest(BaseModel):
    prompt: str

from uuid import uuid4
from typing import Optional

class ThreadManager:
    def __init__(self):
        self.threads = {}

    def create_thread(self):
        thread_id = f"thread_{str(uuid4())}"
        self.threads[thread_id] = []
        return thread_id

    def add_message(self, thread_id, message):
        if thread_id not in self.threads:
            raise ValueError(f"Thread {thread_id} does not exist.")
        
        message_id = f"message_{str(uuid4())}"

        if message["role"] == "system":
            self.threads[thread_id].append(message)
            return message_id
        
        message["message_id"] = message_id
        self.threads[thread_id].append(message)
        return message_id

    def get_thread_messages(self, thread_id):
        if thread_id not in self.threads:
            raise ValueError(f"Thread {thread_id} does not exist.")
        return self.threads[thread_id]

thread_manager = ThreadManager()

class PromptRequest(BaseModel):
    prompt: str
    thread_id: Optional[str] = None

@app.post("/generate")
async def generate_response(request: Request, prompt_request: PromptRequest):
    # global input_messages

    # print(dir(request))
    # print(await request.json())
    
    if prompt_request.thread_id and prompt_request.thread_id in thread_manager.threads:
        thread_id = prompt_request.thread_id
        try:
            thread_messages = thread_manager.get_thread_messages(thread_id)
            input_messages = [{"role": i["role"], "content": i["content"]} for i in thread_messages]
        except ValueError:
            return {"error": f"Thread {thread_id} not found"}
    elif prompt_request.thread_id:
        return {"error": f"Thread {prompt_request.thread_id} not found"}
    else:
        thread_id = thread_manager.create_thread()
        input_messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            }
        ]
        thread_manager.add_message(thread_id, input_messages[0])

    new_input_message = {"role": "user", "content": prompt_request.prompt}
    thread_manager.add_message(thread_id, new_input_message)

    # only append role and content from the new_input_message
    input_messages.append({
        "role": new_input_message["role"],
        "content": new_input_message["content"]
    })

    print(f"Input Messages: {input_messages}")

    new_response = client.responses.create(
        model="gpt-4o-mini",
        instructions=SYSTEM_PROMPT,
        input=input_messages,
        tools=tools,
        tool_choice="auto"
    )

    new_response, input_messages  = process_tool_calls(new_response, input_messages)
    new_assistant_message = {"role": "assistant", "content": new_response.output_text}

    # append the model output to the input messages for next request
    input_messages.append({"role": "assistant", "content": new_response.output_text})

    # append the assistant output to the thread
    thread_manager.add_message(thread_id, new_assistant_message)
    
    return {
        "response": new_response.output_text, 
        "thread_id": thread_id, 
        # "input_messages": input_messages
    }

import uvicorn
# Start the FastAPI server
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=9000)
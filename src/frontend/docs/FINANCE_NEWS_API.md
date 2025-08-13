# Finance News API Setup

This document explains how to set up the finance news APIs for dynamic example prompts.

## Overview

The application now fetches real-time finance news from external APIs and converts them into example prompts for new chats. This provides users with current, relevant finance topics to explore.

## Supported APIs

### 1. Alpha Vantage News API
- **URL**: https://www.alphavantage.co/
- **Free Tier**: 500 requests per day
- **Setup**: 
  1. Sign up at https://www.alphavantage.co/support/#api-key
  2. Get your free API key
  3. Add to `.env.local`: `ALPHA_VANTAGE_API_KEY=your_api_key_here`

### 2. NewsAPI
- **URL**: https://newsapi.org/
- **Free Tier**: 1,000 requests per day
- **Setup**:
  1. Sign up at https://newsapi.org/register
  2. Get your free API key
  3. Add to `.env.local`: `NEWS_API_KEY=your_api_key_here`

## Environment Variables

Add these to your `.env.local` file:

```bash
# Alpha Vantage API (optional)
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_api_key

# NewsAPI (optional)
NEWS_API_KEY=your_news_api_key
```

## How It Works

1. When a user starts a new chat, the system fetches finance news from available APIs
2. The news headlines are converted into example prompts like "Analyze [headline]"
3. If APIs are unavailable or fail, the system falls back to predefined finance prompts
4. Users can click on any example prompt to start a conversation about that topic

## Fallback Messages

If all APIs fail, the system uses these predefined finance prompts:
- Bitcoin price analysis and market trends
- Tesla stock technical analysis
- Best fintech stocks to invest
- Forex trading strategies for beginners

## API Priority

The system tries APIs in this order:
1. Alpha Vantage News API
2. NewsAPI
3. Fallback messages

## Error Handling

- If an API fails, the system automatically tries the next one
- If all APIs fail, it uses fallback messages
- Loading states are shown while fetching
- All errors are logged for debugging

## Customization

You can modify the API sources by editing `app/api/finance-news/route.ts`:
- Add new APIs to the `apis` array
- Modify the `transform` functions to change how headlines are converted to prompts
- Update fallback messages in the `fallbackMessages` array 
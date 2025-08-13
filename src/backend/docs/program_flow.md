# Token Insights Server - Program Flow Documentation

## Overview
This document provides a high-level overview of how the Token Insights Server processes user prompts and generates insights about tokens and cryptocurrencies.

![Program Flow Diagram](program_flow_diagram.png)

## Main Flow (v4/process-prompt)

### 1. Request Handling
- Endpoint: `/v4/process-prompt`
- Input: User prompt and optional thread_id
- Authentication: Requires wallet address and session ID

### 2. Initial Processing
1. **Authentication & Validation**
   - Verifies user authentication
   - Validates that prompt is not empty
   - Checks rate limits for the session

2. **User & Thread Management**
   - Handles user session
   - Creates or retrieves existing thread
   - Manages conversation history

### 3. Agent Pipeline
The system uses a multi-agent approach to process the request:

1. **Research Planning**
   - Uses `planner_agent` to create a research plan
   - Considers previous context if available
   - Determines what information needs to be gathered

2. **Analysis Phase**
   - `CryptoFundManager` agent executes the research plan
   - Gathers token data and market information
   - Performs technical and fundamental analysis

3. **Report Generation**
   Two possible paths:
   - **Token-specific Report**: If token data is available
     - Uses `ReportingAgent` to generate detailed token analysis
     - Includes fundamental data, OHLCV, and technical indicators
   - **Web-based Report**: If no specific token data
     - Uses `WebAgent` to generate insights from web research
     - Focuses on general market information and trends

### 4. Response Structure
The final response includes:
- Original query
- Token metadata (if available)
- Generated insights
- Thread ID for conversation continuity

## Supporting Services

### Rate Limiting
- Prevents API abuse
- Tracks usage per session

### Thread Management
- Maintains conversation context
- Stores message history
- Enables continuous conversations

### Message History
- Endpoints for retrieving message history
- Support for both session-specific and wallet-wide history
- Ability to clear history

## Error Handling
- Comprehensive error catching at each stage
- Graceful fallback to web-based reporting if token analysis fails
- Detailed error logging and tracing

## Additional Features
- Health check endpoint
- Token metrics endpoint for specific token queries
- Session management
- Message history management 
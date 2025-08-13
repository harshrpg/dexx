```mermaid
flowchart TD
 subgraph Crypto_Fund_Manager["Crypto_Fund_Manager"]
        D["Data Access Agent"]
        C["Crypto Fund Manager"]
        E["Web Search Agent"]
        F["Technical Strategist"]
        G["Reporting Agent"]
  end
    A["Agent Manager"] -- User Query --> B["Planner Agent"]
    B -- Research Plan --> C
    C -- Token Data Request --> D
    C -- Web Search Request --> E
    C -- Technical Analysis --> F
    C -- Final Report --> G
    D -- If no data --> E
    D -- If data available --> F
    F --> G
    E --> G

     E:::Peach
    classDef Peach stroke-width:1px, stroke-dasharray:none, stroke:#FBB35A, fill:#FFEFDB, color:#8F632D
    style D fill:#fbb,stroke:#333,stroke-width:2px
    style C fill:#bfb,stroke:#333,stroke-width:2px
    style E fill:#FFE0B2,stroke:#333,stroke-width:2px
    style F fill:#fbb,stroke:#333,stroke-width:2px
    style G fill:#fbb,stroke:#333,stroke-width:2px
    style A fill:#f9f,stroke:#333,stroke-width:2px
    style B fill:#bbf,stroke:#333,stroke-width:2px



```

# Agent Flow Explanation

## 1. AgentManager to Planner Agent
- **Trigger**: User submits a query
- **Action**: Planner Agent analyzes if query is crypto-specific
- **Output**: Creates research plan with API data collection or web search fallback

## 2. Planner to Crypto Fund Manager
- **Trigger**: Receives research plan
- **Action**: Coordinates between sub-agents based on plan type
- **Handoff Rules**: Never performs multiple handoffs - chooses either API or web search path

## 3a. Data Access Agent
- **Trigger**: Crypto-specific query with token details
- **Action**: Fetches data from Mobula and CryptoPanic APIs
- **Handoff**: If no data, hands off to Web Search Agent

## 3b. Web Search Agent
- **Trigger**: Non-crypto query or API data unavailable
- **Action**: Performs web search using fallback plan
- **Output**: Provides web-based insights

## 4. Technical Strategist
- **Trigger**: Valid API data available
- **Action**: Calculates technical indicators and risk scores
- **Output**: Technical analysis with risk assessment

## 5. Reporting Agent
- **Trigger**: Receives data from either path
- **Action**: Generates final analysis report
- **Output**: Structured market analysis with recommendations 
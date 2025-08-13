import { NextResponse } from 'next/server'

interface ExampleMessage {
    heading: string
    message: string
}

// Fallback messages in case all APIs fail
const fallbackMessages: ExampleMessage[] = [
    {
        heading: 'Bitcoin price analysis and market trends',
        message: 'Bitcoin price analysis and market trends'
    },
    {
        heading: 'Tesla stock technical analysis',
        message: 'Tesla stock technical analysis'
    },
    {
        heading: 'Best fintech stocks to invest',
        message: 'Best fintech stocks to invest'
    },
    {
        heading: 'Forex trading strategies for beginners',
        message: 'Forex trading strategies for beginners'
    }
]

// Function to clean and truncate headlines
function cleanHeadline(headline: string): string {
    // Remove common prefixes and clean up the text
    let cleaned = headline
        .replace(/^(Breaking|Latest|Update|News):\s*/i, '')
        .replace(/^(Reuters|Bloomberg|CNBC|MarketWatch):\s*/i, '')
        .replace(/\s*-\s*(Reuters|Bloomberg|CNBC|MarketWatch)$/i, '')
        .trim()

    // Truncate to reasonable length (around 60 characters)
    if (cleaned.length > 60) {
        cleaned = cleaned.substring(0, 57) + '...'
    }

    return cleaned
}

async function fetchFinanceNews(): Promise<ExampleMessage[]> {
    try {
        // Try multiple free finance news APIs
        const apis = [
            // Alpha Vantage News API (free tier available)
            {
                url: `https://www.alphavantage.co/query?function=NEWS_SENTIMENT&topics=technology&apikey=${process.env.ALPHA_VANTAGE_API_KEY || 'demo'}`,
                transform: (data: any) => {
                    if (data.feed && Array.isArray(data.feed)) {
                        return data.feed.slice(0, 4).map((item: any) => ({
                            heading: cleanHeadline(item.title),
                            message: `Analyze ${cleanHeadline(item.title)}`
                        }))
                    }
                    return []
                }
            },
            // NewsAPI (free tier available)
            {
                url: `https://newsapi.org/v2/top-headlines?category=business&language=en&apiKey=${process.env.NEWS_API_KEY || 'demo'}`,
                transform: (data: any) => {
                    if (data.articles && Array.isArray(data.articles)) {
                        return data.articles.slice(0, 4).map((item: any) => ({
                            heading: cleanHeadline(item.title),
                            message: `Analyze ${cleanHeadline(item.title)}`
                        }))
                    }
                    return []
                }
            }
        ]

        for (const api of apis) {
            try {
                const response = await fetch(api.url, {
                    headers: {
                        'User-Agent': 'Mozilla/5.0 (compatible; FinanceBot/1.0)'
                    }
                })

                if (response.ok) {
                    const data = await response.json()
                    const transformed = api.transform(data)
                    if (transformed.length > 0) {
                        return transformed
                    }
                }
            } catch (error) {
                console.warn('API fetch failed, trying next:', error)
                continue
            }
        }

        // If all APIs fail, return fallback
        return fallbackMessages
    } catch (error) {
        console.error('All finance news APIs failed:', error)
        return fallbackMessages
    }
}

export async function GET() {
    try {
        const news = await fetchFinanceNews()
        return NextResponse.json({ messages: news })
    } catch (error) {
        console.error('Failed to fetch finance news:', error)
        return NextResponse.json({ messages: fallbackMessages })
    }
} 
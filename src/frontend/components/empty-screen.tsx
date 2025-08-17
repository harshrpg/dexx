import { Button } from '@/components/ui/button'
import { ArrowRight } from 'lucide-react'
import { useEffect, useMemo, useState } from 'react'

interface ExampleMessage {
  heading: string
  message: string
}

// Fallback messages in case API fails
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

async function fetchFinanceNews(): Promise<ExampleMessage[]> {
  try {
    const response = await fetch('/api/finance-news')
    if (response.ok) {
      const data = await response.json()
      return data.messages || fallbackMessages
    }
    return fallbackMessages
  } catch (error) {
    console.error('Failed to fetch finance news:', error)
    return fallbackMessages
  }
}

function makeSymbolSuggestions(symbol: string): ExampleMessage[] {
  const s = symbol.trim()
  return [
    {
      heading: `${s}: technical outlook and key levels today`,
      message: `Provide a concise technical outlook for ${s} with key support/resistance, trend bias, and potential setups`
    },
    {
      heading: `${s}: latest news and catalysts`,
      message: `Summarize the most recent news and catalysts impacting ${s} and how they might affect price`
    },
    {
      heading: `${s}: indicators to watch now`,
      message: `For ${s}, recommend the most relevant technical indicators right now (with parameters) and how to interpret them`
    },
    {
      heading: `${s}: risk management and invalidation`,
      message: `For ${s}, propose a risk-managed trade idea with entry/targets/stop and clear invalidation criteria`
    }
  ]
}

export function EmptyScreen({
  submitMessage,
  className,
  symbol
}: {
  submitMessage: (message: string) => void
  className?: string
  symbol?: string
}) {
  const [exampleMessages, setExampleMessages] = useState<ExampleMessage[]>(fallbackMessages)
  const [isLoading, setIsLoading] = useState(true)

  const hasSymbol = useMemo(() => Boolean(symbol && symbol.trim().length > 0), [symbol])

  useEffect(() => {
    let mounted = true
    async function load() {
      setIsLoading(true)
      try {
        if (hasSymbol && symbol) {
          const suggestions = makeSymbolSuggestions(symbol)
          if (mounted) setExampleMessages(suggestions)
        } else {
          const news = await fetchFinanceNews()
          if (mounted) setExampleMessages(news)
        }
      } catch (error) {
        console.error('Failed to load suggestions:', error)
        if (mounted) setExampleMessages(fallbackMessages)
      } finally {
        if (mounted) setIsLoading(false)
      }
    }
    load()
    return () => {
      mounted = false
    }
  }, [hasSymbol, symbol])

  return (
    <div className={`mx-auto w-full transition-all ${className}`}>
      <div className="bg-background p-2">
        <div className="mt-2 flex flex-col items-start space-y-2 mb-4">
          {isLoading ? (
            // Loading skeleton
            Array.from({ length: 4 }).map((_, index) => (
              <div
                key={index}
                className="h-6 bg-muted animate-pulse rounded w-3/4"
              />
            ))
          ) : (
            exampleMessages.map((message, index) => (
              <Button
                key={index}
                variant="link"
                className="h-auto p-0 text-base text-left justify-start max-w-full group"
                name={message.message}
                onClick={async () => {
                  submitMessage(message.message)
                }}
                title={message.heading}
              >
                <ArrowRight size={16} className="mr-2 text-muted-foreground flex-shrink-0" />
                <span className="truncate block max-w-[calc(100%-24px)] leading-relaxed">
                  {message.heading}
                </span>
              </Button>
            ))
          )}
        </div>
      </div>
    </div>
  )
}


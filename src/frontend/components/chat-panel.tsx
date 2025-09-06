'use client'

import { Model } from '@/lib/types/models'
import { cn } from '@/lib/utils'
import { Message } from 'ai'
import { ArrowUp, ChevronDown, MessageCirclePlus, Square } from 'lucide-react'
import { useRouter } from 'next/navigation'
import { useEffect, useRef, useState } from 'react'
import Textarea from 'react-textarea-autosize'
import { useArtifact } from './artifact/artifact-context'
import { EmptyScreen } from './empty-screen'
import { ModelSelector } from './model-selector'
import { SearchModeToggle } from './search-mode-toggle'
import { Button } from './ui/button'
import { IconLogo } from './ui/icons'
import { AdvancedAiSwitch } from './advanced-ai-switch'
import { SymbolSelect } from './symbol-select'
import type { SymbolSearchItem } from '@/lib/tradingview/symbols'
import { fetchAllSymbols } from '@/lib/tradingview/symbols'
import { setCookie } from '@/lib/utils/cookies'
import { useAppDispatch } from '@/lib/store/hooks'
import { set } from '@/features/advanced-mode/advancedModeSlice'
import { AdvancedModeState } from '@/types/chatInput'

interface ChatPanelProps {
  input: string
  handleInputChange: (e: React.ChangeEvent<HTMLTextAreaElement>) => void
  handleSubmit: (e: React.FormEvent<HTMLFormElement>) => void
  isLoading: boolean
  messages: Message[]
  setMessages: (messages: Message[]) => void
  query?: string
  stop: () => void
  append: (message: any) => void
  models?: Model[]
  /** Whether to show the scroll to bottom button */
  showScrollToBottomButton: boolean
  /** Reference to the scroll container */
  scrollContainerRef: React.RefObject<HTMLDivElement>
  advancedModeValues?: AdvancedModeState
}

export function ChatPanel({
  input,
  handleInputChange,
  handleSubmit,
  isLoading,
  messages,
  setMessages,
  query,
  stop,
  append,
  models,
  showScrollToBottomButton,
  scrollContainerRef,
  advancedModeValues
}: ChatPanelProps) {
  const [showEmptyScreen, setShowEmptyScreen] = useState(false)
  const router = useRouter()
  const inputRef = useRef<HTMLTextAreaElement>(null)
  const isFirstRender = useRef(true)
  const [isComposing, setIsComposing] = useState(false) // Composition state
  const [enterDisabled, setEnterDisabled] = useState(false) // Disable Enter after composition ends
  const { close: closeArtifact } = useArtifact()

  // Advanced AI mode state
  const [advancedEnabled, setAdvancedEnabled] = useState<boolean>(advancedModeValues?.value || false)
  const [advancedSymbol, setAdvancedSymbol] = useState<string>(advancedModeValues?.symbol || 'BTC/USD')
  const [symbolOptions, setSymbolOptions] = useState<SymbolSearchItem[] | null>(null)
  const [symbolsLoading, setSymbolsLoading] = useState<boolean>(false)

  const dispatch = useAppDispatch();

  // Prefetch symbols on first render
  useEffect(() => {
    let mounted = true
    if (!symbolOptions) {
      setSymbolsLoading(true)
      fetchAllSymbols().then((opts) => {
        if (mounted) setSymbolOptions(opts)
      }).finally(() => mounted && setSymbolsLoading(false))
    }
    return () => { mounted = false }
  }, [symbolOptions])

  const handleCompositionStart = () => setIsComposing(true)

  const handleCompositionEnd = () => {
    setIsComposing(false)
    setEnterDisabled(true)
    setTimeout(() => {
      setEnterDisabled(false)
    }, 300)
  }

  const handleNewChat = () => {
    setMessages([])
    closeArtifact()
    router.push('/')
  }

  const isToolInvocationInProgress = () => {
    if (!messages.length) return false

    const lastMessage = messages[messages.length - 1]
    if (lastMessage.role !== 'assistant' || !lastMessage.parts) return false

    const parts = lastMessage.parts
    const lastPart = parts[parts.length - 1]

    return (
      lastPart?.type === 'tool-invocation' &&
      lastPart?.toolInvocation?.state === 'call'
    )
  }

  // if query is not empty, submit the query
  useEffect(() => {
    if (isFirstRender.current && query && query.trim().length > 0) {
      append({
        role: 'user',
        content: query
      })
      isFirstRender.current = false
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [query])

  // When Advanced toggles, write cookie readable by API
  useEffect(() => {
    try {
      setCookie('advanced-mode-enabled', String(advancedEnabled))
      setCookie('advanced-mode-symbol', advancedSymbol)
    } catch {
      throw Error('Unable to store advanced mode cookies');
    }
    const advancedModeValue: AdvancedModeState = {
      value: advancedEnabled,
      symbol: advancedSymbol
    }
    dispatch(set(advancedModeValue));
  }, [advancedEnabled, advancedSymbol])

  // Scroll to the bottom of the container
  const handleScrollToBottom = () => {
    const scrollContainer = scrollContainerRef.current
    if (scrollContainer) {
      scrollContainer.scrollTo({
        top: scrollContainer.scrollHeight,
        behavior: 'smooth'
      })
    }
  }

  return (
    <div
      className={cn(
        'w-full bg-background group/form-container shrink-0',
        messages.length > 0 ? 'sticky bottom-0 px-2 pb-4' : 'px-6'
      )}
    >
      {messages.length === 0 && (
        <div className="mb-10 flex flex-col items-center gap-4">
          <IconLogo className="size-12 text-muted-foreground" />
          <p className="text-center text-3xl font-semibold">
            How can I help you today?
          </p>
        </div>
      )}
      <form
        onSubmit={handleSubmit}
        className={cn('max-w-3xl w-full mx-auto relative')}
      >
        {/* Scroll to bottom button - only shown when showScrollToBottomButton is true */}
        {showScrollToBottomButton && messages.length > 0 && (
          <Button
            type="button"
            variant="outline"
            size="icon"
            className="absolute -top-10 right-4 z-20 size-8 rounded-full shadow-md"
            onClick={handleScrollToBottom}
            title="Scroll to bottom"
          >
            <ChevronDown size={16} />
          </Button>
        )}

        {advancedEnabled ? (
          <div className="rounded-3xl p-[1px] bg-gradient-to-r from-purple-500 via-fuchsia-500 to-blue-500">
            <div className="relative flex flex-col w-full gap-2 bg-muted rounded-3xl border border-input">
              <div className='m-4'>
                <AdvancedAiSwitch
                  enabled={advancedEnabled}
                  onEnabledChange={setAdvancedEnabled}
                />
              </div>

              <Textarea
                ref={inputRef}
                name="input"
                rows={2}
                maxRows={5}
                tabIndex={0}
                onCompositionStart={handleCompositionStart}
                onCompositionEnd={handleCompositionEnd}
                placeholder="Ask a question..."
                spellCheck={false}
                value={input}
                disabled={isLoading || isToolInvocationInProgress()}
                className="resize-none w-full min-h-12 bg-transparent border-0 p-4 text-sm placeholder:text-muted-foreground focus-visible:outline-none disabled:cursor-not-allowed disabled:opacity-50"
                onChange={e => {
                  handleInputChange(e)
                  setShowEmptyScreen(e.target.value.length === 0)
                }}
                onKeyDown={e => {
                  if (
                    e.key === 'Enter' &&
                    !e.shiftKey &&
                    !isComposing &&
                    !enterDisabled
                  ) {
                    if (input.trim().length === 0) {
                      e.preventDefault()
                      return
                    }
                    e.preventDefault()
                    const textarea = e.target as HTMLTextAreaElement
                    textarea.form?.requestSubmit()
                  }
                }}
                onFocus={() => setShowEmptyScreen(true)}
                onBlur={() => setShowEmptyScreen(false)}
              />

              {/* Bottom menu area */}
              <div className="flex items-center justify-between p-3">
                <div className="flex items-center gap-2">
                  <ModelSelector models={models || []} />
                  <SearchModeToggle />
                  <SymbolSelect
                    value={advancedSymbol}
                    onChange={setAdvancedSymbol}
                    disabled={!advancedEnabled}
                    options={symbolOptions ?? undefined}
                    loading={symbolsLoading}
                  />
                </div>
                <div className="flex items-center gap-2">
                  {messages.length > 0 && (
                    <Button
                      variant="outline"
                      size="icon"
                      onClick={handleNewChat}
                      className="shrink-0 rounded-full group"
                      type="button"
                      disabled={isLoading || isToolInvocationInProgress()}
                    >
                      <MessageCirclePlus className="size-4 group-hover:rotate-12 transition-all" />
                    </Button>
                  )}
                  <Button
                    type={isLoading ? 'button' : 'submit'}
                    size={'icon'}
                    variant={'outline'}
                    className={cn(isLoading && 'animate-pulse', 'rounded-full')}
                    disabled={
                      (input.length === 0 && !isLoading) ||
                      isToolInvocationInProgress()
                    }
                    onClick={isLoading ? stop : undefined}
                  >
                    {isLoading ? <Square size={20} /> : <ArrowUp size={20} />}
                  </Button>
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="relative flex flex-col w-full gap-2 bg-muted rounded-3xl border border-input">
            <div className='m-4'>
              <AdvancedAiSwitch enabled={advancedEnabled} onEnabledChange={setAdvancedEnabled} />
            </div>
            <Textarea
              ref={inputRef}
              name="input"
              rows={2}
              maxRows={5}
              tabIndex={0}
              onCompositionStart={handleCompositionStart}
              onCompositionEnd={handleCompositionEnd}
              placeholder="Ask a question..."
              spellCheck={false}
              value={input}
              disabled={isLoading || isToolInvocationInProgress()}
              className="resize-none w-full min-h-12 bg-transparent border-0 p-4 text-sm placeholder:text-muted-foreground focus-visible:outline-none disabled:cursor-not-allowed disabled:opacity-50"
              onChange={e => {
                handleInputChange(e)
                setShowEmptyScreen(e.target.value.length === 0)
              }}
              onKeyDown={e => {
                if (
                  e.key === 'Enter' &&
                  !e.shiftKey &&
                  !isComposing &&
                  !enterDisabled
                ) {
                  if (input.trim().length === 0) {
                    e.preventDefault()
                    return
                  }
                  e.preventDefault()
                  const textarea = e.target as HTMLTextAreaElement
                  textarea.form?.requestSubmit()
                }
              }}
              onFocus={() => setShowEmptyScreen(true)}
              onBlur={() => setShowEmptyScreen(false)}
            />

            {/* Bottom menu area */}
            <div className='p-3'>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <ModelSelector models={models || []} />
                  <SearchModeToggle />

                  <SymbolSelect
                    value={advancedSymbol}
                    onChange={setAdvancedSymbol}
                    disabled={!advancedEnabled}
                    options={symbolOptions ?? undefined}
                    loading={symbolsLoading}
                  />
                </div>
                <div className="flex items-center gap-2">
                  {messages.length > 0 && (
                    <Button
                      variant="outline"
                      size="icon"
                      onClick={handleNewChat}
                      className="shrink-0 rounded-full group"
                      type="button"
                      disabled={isLoading || isToolInvocationInProgress()}
                    >
                      <MessageCirclePlus className="size-4 group-hover:rotate-12 transition-all" />
                    </Button>
                  )}
                  <Button
                    type={isLoading ? 'button' : 'submit'}
                    size={'icon'}
                    variant={'outline'}
                    className={cn(isLoading && 'animate-pulse', 'rounded-full')}
                    disabled={
                      (input.length === 0 && !isLoading) ||
                      isToolInvocationInProgress()
                    }
                    onClick={isLoading ? stop : undefined}
                  >
                    {isLoading ? <Square size={20} /> : <ArrowUp size={20} />}
                  </Button>
                </div>
              </div>
            </div>

          </div>
        )}

        {messages.length === 0 && (
          <EmptyScreen
            submitMessage={message => {
              handleInputChange({
                target: { value: message }
              } as React.ChangeEvent<HTMLTextAreaElement>)
            }}
            className={cn(showEmptyScreen ? 'visible' : 'invisible')}
            symbol={advancedEnabled ? advancedSymbol : undefined}
          />
        )}
      </form>
    </div>
  )
}

"use client"

import { cn } from '@/lib/utils'
import { usePathname } from 'next/navigation'
import { useEffect, useMemo, useState } from 'react'
import { ChatHistoryClient } from './chat-history-client'

function extractChatIdFromPath(pathname: string | null): string | null {
    if (!pathname) return null
    // Expecting /search/[id]
    const match = pathname.match(/^\/search\/([^\/]+)(?:$|\?)/)
    return match ? match[1] : null
}

export function ChatSidebarTabs() {
    const pathname = usePathname()
    const chatId = useMemo(() => extractChatIdFromPath(pathname), [pathname])
    const [advancedActive, setAdvancedActive] = useState<boolean>(false)
    const [activeTab, setActiveTab] = useState<'history' | 'conversation'>('conversation')
    const [bootMessages, setBootMessages] = useState<Array<{ id?: string; role: string; content: string }> | null>(null)

    // Initialize from persisted state
    useEffect(() => {
        try {
            const saved = localStorage.getItem('advanced-mode-enabled')
            if (saved != null) {
                const enabled = JSON.parse(saved) === true
                setAdvancedActive(enabled)
                if (enabled) {
                    setActiveTab('conversation')
                    const cached = (window as any).__chat_messages as Array<{ id?: string; role: string; content: string }> | undefined
                    if (cached && cached.length) setBootMessages(cached)
                }
            }
        } catch { }
    }, [])

    // Listen to advanced mode changes
    useEffect(() => {
        const handler = (e: Event) => {
            const ce = e as CustomEvent<{ enabled: boolean }>
            setAdvancedActive(!!ce.detail.enabled)
            if (ce.detail.enabled) setActiveTab('conversation')
        }
        window.addEventListener('advanced-mode-changed', handler as EventListener)
        return () => window.removeEventListener('advanced-mode-changed', handler as EventListener)
    }, [])

    // Also listen to storage updates across tabs
    useEffect(() => {
        const onStorage = (e: StorageEvent) => {
            if (e.key === 'advanced-mode-enabled' && e.newValue != null) {
                const val = (() => { try { return JSON.parse(e.newValue!) } catch { return false } })()
                setAdvancedActive(val === true)
                if (val === true) setActiveTab('conversation')
            }
        }
        window.addEventListener('storage', onStorage)
        return () => window.removeEventListener('storage', onStorage)
    }, [])

    // If no chat open or not advanced -> show history only
    if (!chatId || !advancedActive) {
        return <ChatHistoryClient />
    }

    return (
        <div className="flex flex-col h-full">
            {/* Tab list */}
            <div className="px-2 pb-2">
                <div className="inline-flex rounded-full border border-input bg-background p-1 text-xs">
                    <button
                        onClick={() => setActiveTab('history')}
                        className={cn(
                            'px-3 py-1 rounded-full transition-colors',
                            activeTab === 'history'
                                ? 'bg-accent text-accent-foreground'
                                : 'text-muted-foreground hover:bg-muted'
                        )}
                    >
                        History
                    </button>
                    <button
                        onClick={() => setActiveTab('conversation')}
                        className={cn(
                            'px-3 py-1 rounded-full transition-colors',
                            activeTab === 'conversation'
                                ? 'bg-accent text-accent-foreground'
                                : 'text-muted-foreground hover:bg-muted'
                        )}
                    >
                        Conversation
                    </button>
                </div>
            </div>

            <div className="flex-1 min-h-0">
                {activeTab === 'history' ? (
                    <ChatHistoryClient />
                ) : (
                    <SidebarConversation bootMessages={bootMessages || undefined} />
                )}
            </div>
        </div>
    )
}

function SidebarConversation({ bootMessages }: { bootMessages?: Array<{ id?: string; role: string; content: string }> }) {
    const [messages, setMessages] = useState<Array<{ id?: string; role: string; content: string }>>([])

    useEffect(() => {
        if (bootMessages && bootMessages.length) setMessages(bootMessages)
        const handler = (e: Event) => {
            const ce = e as CustomEvent<{ chatId: string; messages: Array<{ id?: string; role: string; content: string }> }>
            setMessages(ce.detail.messages)
        }
        window.addEventListener('chat-messages-updated', handler as EventListener)
        return () => window.removeEventListener('chat-messages-updated', handler as EventListener)
    }, [bootMessages])

    if (!messages || messages.length === 0) {
        return (
            <div className="px-3 py-4 text-sm text-muted-foreground">
                No conversation yet.
            </div>
        )
    }

    return (
        <div className="flex flex-col h-full">
            <div className="flex-1 overflow-y-auto px-2 pb-2">
                <ul className="flex flex-col gap-2">
                    {messages.map((m, idx) => (
                        <li key={m.id ?? idx} className={cn('rounded-lg p-2 border text-xs', m.role === 'user' ? 'bg-background' : 'bg-muted')}>
                            <div className="mb-1 font-medium text-foreground/70">{m.role === 'user' ? 'You' : 'Assistant'}</div>
                            <div className="whitespace-pre-wrap text-foreground/90 leading-relaxed">
                                {truncate(m.content, 500)}
                            </div>
                        </li>
                    ))}
                </ul>
            </div>
        </div>
    )
}

function truncate(text: string, max: number) {
    if (text.length <= max) return text
    return text.slice(0, max - 1) + '…'
} 
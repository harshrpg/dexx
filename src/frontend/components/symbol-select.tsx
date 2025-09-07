"use client"

import { useEffect, useMemo, useState } from 'react'
import { Button } from './ui/button'
import { Popover, PopoverContent, PopoverTrigger } from './ui/popover'
import { Command, CommandEmpty, CommandGroup, CommandInput, CommandItem, CommandList } from './ui/command'
import { fetchAllSymbols, type SymbolSearchItem } from '@/lib/tradingview/symbols'
import { ChevronsUpDown, Check } from 'lucide-react'

interface SymbolSelectProps {
    value: string
    onChange: (symbol: string) => void
    disabled?: boolean
    className?: string
    placeholder?: string
    options?: SymbolSearchItem[]
    loading?: boolean
}

export function SymbolSelect({ value, onChange, disabled, className, placeholder = 'Select symbol', options, loading: externalLoading }: SymbolSelectProps) {
    const [open, setOpen] = useState(false)
    const [loadingInternal, setLoadingInternal] = useState(false)
    const [symbolsInternal, setSymbolsInternal] = useState<SymbolSearchItem[]>([])
    const [query, setQuery] = useState('')

    const shouldUseInternal = !options || options.length === 0

    // Load symbols when opening for the first time if no options provided
    useEffect(() => {
        if (!shouldUseInternal) return
        if (!open || symbolsInternal.length > 0) return
        setLoadingInternal(true)
        fetchAllSymbols()
            .then(setSymbolsInternal)
            .finally(() => setLoadingInternal(false))
    }, [open, symbolsInternal.length, shouldUseInternal])

    const source = shouldUseInternal ? symbolsInternal : options!
    const loading = shouldUseInternal ? loadingInternal : Boolean(externalLoading)

    const filtered = useMemo(() => {
        const base = source
        if (!query) return base.slice(0, 500)
        const q = query.toLowerCase()
        return base
            .filter(s => `${s.exchange}:${s.ticker}`.toLowerCase().includes(q) || s.ticker.toLowerCase().includes(q))
            .slice(0, 500)
    }, [source, query])

    const groupedByExchange = useMemo(() => {
        return filtered.reduce((groups, item) => {
            const exch = item.exchange || 'Other'
            if (!groups[exch]) groups[exch] = [] as SymbolSearchItem[]
            groups[exch].push(item)
            return groups
        }, {} as Record<string, SymbolSearchItem[]>)
    }, [filtered])

    return (
        <Popover open={open} onOpenChange={setOpen}>
            <PopoverTrigger asChild>
                <Button
                    variant="outline"
                    role="combobox"
                    aria-expanded={open}
                    className={`text-sm rounded-full shadow-none focus:ring-0 ${className ?? ''}`}
                    disabled={disabled}
                >
                    {value ? (
                        <span className="text-xs font-medium">{value}</span>
                    ) : (
                        placeholder
                    )}
                    <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
                </Button>
            </PopoverTrigger>
            <PopoverContent className="w-72 p-0" align="start">
                <Command>
                    <CommandInput placeholder="Search symbols..." value={query} onValueChange={setQuery} />
                    <CommandList>
                        <CommandEmpty>{loading ? 'Loading…' : 'No symbol found.'}</CommandEmpty>
                        {Object.entries(groupedByExchange).map(([exchange, items]) => (
                            <CommandGroup key={exchange} heading={exchange}>
                                {items.map((s) => (
                                    <CommandItem
                                        key={`${s.exchange}:${s.ticker}`}
                                        value={s.ticker}
                                        onSelect={(v) => {
                                            onChange(v)
                                            setOpen(false)
                                        }}
                                        className="flex justify-between"
                                    >
                                        <span className="text-xs font-medium">{s.ticker}</span>
                                        <Check className={`h-4 w-4 ${value === s.ticker ? 'opacity-100' : 'opacity-0'}`} />
                                    </CommandItem>
                                ))}
                            </CommandGroup>
                        ))}
                    </CommandList>
                </Command>
            </PopoverContent>
        </Popover>
    )
} 
"use client"

import { Switch } from './ui/switch'

interface AdvancedAiSwitchProps {
    enabled: boolean
    onEnabledChange: (enabled: boolean) => void
    className?: string
}

export function AdvancedAiSwitch({ enabled, onEnabledChange, className }: AdvancedAiSwitchProps) {
    return (
        <div className={`inline-flex items-center gap-2 rounded-lg border px-2 py-1 ${className ?? ''}`}>
            <span className="text-xs text-muted-foreground">Advanced</span>
            <Switch size="sm" checked={enabled} onCheckedChange={v => onEnabledChange(Boolean(v))} className="border" />
        </div>
    )
}
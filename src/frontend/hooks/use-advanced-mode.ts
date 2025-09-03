'use client'

import { useEffect, useState } from 'react'

export function useAdvancedMode(): boolean {
    const [enabled, setEnabled] = useState(false)

    useEffect(() => {
        try {
            const value = getCookie('advanced-mode-enabled')
            console.log('###### ==> cookie for advanced mode: ', value)
            setEnabled(value === 'true')
        } catch {
            setEnabled(false)
        }
    }, [])

    return enabled
}

function getCookie(name: string): string | null {
    if (typeof document === 'undefined') return null
    const cookies = document.cookie.split(';')
    for (const cookie of cookies) {
        const [cookieName, cookieValue] = cookie.trim().split('=')
        if (cookieName === name) {
            return decodeURIComponent(cookieValue)
        }
    }
    return null
}

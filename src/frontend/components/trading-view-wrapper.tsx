'use client';

import { useEffect, useState } from 'react';
import TradingViewChart from './trading-view-chart';

interface TradingViewWrapperProps {
    symbol?: string;
    interval?: string;
    theme?: 'light' | 'dark';
    width?: number | string;
    height?: number | string;
    fullscreen?: boolean;
    debug?: boolean;
    datafeedUrl?: string;
}

export default function TradingViewWrapper(props: TradingViewWrapperProps) {
    const [isClient, setIsClient] = useState(false);

    useEffect(() => {
        setIsClient(true);
    }, []);

    // Show loading state during SSR and initial hydration
    if (!isClient) {
        return (
            <div
                className="flex items-center justify-center border rounded-lg bg-gray-50 dark:bg-gray-900"
                style={{
                    width: typeof props.width === 'number' ? `${props.width}px` : props.width || '100%',
                    height: typeof props.height === 'number' ? `${props.height}px` : props.height || '600px',
                }}
            >
                <div className="text-center">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto mb-2"></div>
                    <p className="text-sm text-gray-500">Loading TradingView Chart...</p>
                </div>
            </div>
        );
    }

    return <TradingViewChart {...props} />;
} 
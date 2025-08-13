'use client';

import { useEffect, useRef } from 'react';
import type { TradingViewWidgetOptions } from '@/types/tradingview';

interface TradingViewChartProps {
    symbol?: string;
    interval?: string;
    theme?: 'light' | 'dark';
    width?: number | string;
    height?: number | string;
    fullscreen?: boolean;
    debug?: boolean;
    datafeedUrl?: string;
}

export default function TradingViewChart({
    symbol = 'AAPL',
    interval = '1D',
    theme = 'light',
    width = '100%',
    height = '600',
    fullscreen = true,
    debug = true,
    datafeedUrl = 'https://demo-feed-data.tradingview.com'
}: TradingViewChartProps) {
    const containerRef = useRef<HTMLDivElement>(null);
    const widgetRef = useRef<any>(null);

    useEffect(() => {
        // Load TradingView scripts dynamically
        const loadTradingViewScripts = async () => {
            // Check if scripts are already loaded
            if (window.TradingView) {
                return;
            }

            // Load charting library script
            const chartingScript = document.createElement('script');
            chartingScript.src = '/charting_library/charting_library.standalone.js';
            chartingScript.async = true;

            // Load datafeed script
            const datafeedScript = document.createElement('script');
            datafeedScript.src = '/charting_library/datafeeds/udf/dist/bundle.js';
            datafeedScript.async = true;

            // Wait for both scripts to load
            await new Promise<void>((resolve) => {
                let loadedScripts = 0;
                const checkLoaded = () => {
                    loadedScripts++;
                    if (loadedScripts === 2) {
                        resolve();
                    }
                };

                chartingScript.onload = checkLoaded;
                datafeedScript.onload = checkLoaded;

                // Handle errors
                chartingScript.onerror = () => {
                    console.error('Failed to load TradingView charting library');
                    checkLoaded();
                };
                datafeedScript.onerror = () => {
                    console.error('Failed to load TradingView datafeed');
                    checkLoaded();
                };
            });

            document.head.appendChild(chartingScript);
            document.head.appendChild(datafeedScript);
        };

        const initializeWidget = async () => {
            try {
                await loadTradingViewScripts();

                // Wait a bit for scripts to initialize
                await new Promise(resolve => setTimeout(resolve, 100));

                if (!window.TradingView || !containerRef.current) {
                    console.error('TradingView not available or container not found');
                    return;
                }

                // Clean up existing widget
                if (widgetRef.current) {
                    widgetRef.current.remove();
                }

                // Create new widget
                widgetRef.current = new window.TradingView.widget({
                    container: containerRef.current,
                    locale: 'en',
                    library_path: '/charting_library/',
                    datafeed: new window.Datafeeds.UDFCompatibleDatafeed(datafeedUrl),
                    symbol: symbol,
                    interval: interval,
                    fullscreen: fullscreen,
                    debug: debug,
                    width: width,
                    height: height,
                    theme: theme,
                    timezone: 'Etc/UTC',
                    toolbar_bg: theme === 'dark' ? '#131722' : '#f1f3f6',
                    enable_publishing: false,
                    hide_top_toolbar: false,
                    hide_legend: false,
                    save_image: false,
                    backgroundColor: theme === 'dark' ? '#131722' : '#ffffff',
                    gridColor: theme === 'dark' ? '#363c4e' : '#e1e3e6',
                    widthRatio: 1,
                    heightRatio: 1,
                });
            } catch (error) {
                console.error('Error initializing TradingView widget:', error);
            }
        };

        initializeWidget();

        // Cleanup function
        return () => {
            if (widgetRef.current) {
                try {
                    widgetRef.current.remove();
                } catch (error) {
                    console.error('Error removing TradingView widget:', error);
                }
            }
        };
    }, [symbol, interval, theme, width, height, fullscreen, debug, datafeedUrl]);

    return (
        <div
            ref={containerRef}
            className="trading-view-chart"
            style={{
                width: typeof width === 'number' ? `${width}px` : width,
                height: typeof height === 'number' ? `${height}px` : height,
            }}
        />
    );
} 
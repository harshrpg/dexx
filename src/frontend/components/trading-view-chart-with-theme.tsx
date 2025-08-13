'use client';

import { useEffect, useRef, useState } from 'react';
import { useTheme } from 'next-themes';
import type { TradingViewWidgetOptions } from '@/types/tradingview';

interface TradingViewChartWithThemeProps {
    symbol?: string;
    interval?: string;
    width?: number | string;
    height?: number | string;
    fullscreen?: boolean;
    debug?: boolean;
    datafeedUrl?: string;
    showToolbar?: boolean;
    showLegend?: boolean;
    enablePublishing?: boolean;
    customStudies?: any;
    loadingScreen?: any;
}

export default function TradingViewChartWithTheme({
    symbol = 'AAPL',
    interval = '1D',
    width = '100%',
    height = '600',
    fullscreen = true,
    debug = false,
    datafeedUrl = 'https://demo-feed-data.tradingview.com',
    showToolbar = true,
    showLegend = true,
    enablePublishing = false,
    customStudies,
    loadingScreen
}: TradingViewChartWithThemeProps) {
    const containerRef = useRef<HTMLDivElement>(null);
    const widgetRef = useRef<any>(null);
    const { theme, resolvedTheme } = useTheme();
    const [isLoading, setIsLoading] = useState(true);

    // Determine the actual theme to use
    const currentTheme = (resolvedTheme || theme || 'light') as 'light' | 'dark';

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
                setIsLoading(true);
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

                // Theme-specific configurations
                const themeConfig = {
                    light: {
                        backgroundColor: '#ffffff',
                        gridColor: '#e1e3e6',
                        toolbar_bg: '#f1f3f6',
                        textColor: '#131722',
                    },
                    dark: {
                        backgroundColor: '#131722',
                        gridColor: '#363c4e',
                        toolbar_bg: '#131722',
                        textColor: '#d1d4dc',
                    },
                };

                const currentThemeConfig = themeConfig[currentTheme] || themeConfig.light;

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
                    theme: currentTheme,
                    timezone: 'Etc/UTC',
                    toolbar_bg: currentThemeConfig.toolbar_bg,
                    enable_publishing: enablePublishing,
                    hide_top_toolbar: !showToolbar,
                    hide_legend: !showLegend,
                    save_image: false,
                    backgroundColor: currentThemeConfig.backgroundColor,
                    gridColor: currentThemeConfig.gridColor,
                    widthRatio: 1,
                    heightRatio: 1,
                    studies_overrides: customStudies || {},
                    loading_screen: loadingScreen || { backgroundColor: currentThemeConfig.backgroundColor },
                    custom_css_url: '/charting_library/themed.css',
                });

                setIsLoading(false);
            } catch (error) {
                console.error('Error initializing TradingView widget:', error);
                setIsLoading(false);
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
    }, [symbol, interval, currentTheme, width, height, fullscreen, debug, datafeedUrl, showToolbar, showLegend, enablePublishing, customStudies, loadingScreen]);

    if (isLoading) {
        return (
            <div
                className="flex items-center justify-center border rounded-lg"
                style={{
                    width: typeof width === 'number' ? `${width}px` : width,
                    height: typeof height === 'number' ? `${height}px` : height,
                    backgroundColor: currentTheme === 'dark' ? '#131722' : '#ffffff',
                }}
            >
                <div className="text-center">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto mb-2"></div>
                    <p className="text-sm text-gray-500">Loading TradingView Chart...</p>
                </div>
            </div>
        );
    }

    return (
        <div
            ref={containerRef}
            className="trading-view-chart border rounded-lg overflow-hidden"
            style={{
                width: typeof width === 'number' ? `${width}px` : width,
                height: typeof height === 'number' ? `${height}px` : height,
            }}
        />
    );
} 
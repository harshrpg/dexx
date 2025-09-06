'use client';

import { useAppSelector } from "@/lib/store/hooks";
import Datafeed from "@/lib/tradingview/datafeed";
import { loadScript, loadCSS } from "@/lib/tv/utils";
import { useEffect, useRef, useState } from "react";

// Global state to track script loading
let scriptsLoaded = false;
let loadingPromise: Promise<void> | null = null;

const TradingViewWrapper = () => {
    const containerRef = useRef<HTMLDivElement>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const symbol = useAppSelector((s) => s.advancedMode.symbol);

    useEffect(() => {
        let isMounted = true;
        let widget: any = null;

        const loadScripts = async () => {
            if (scriptsLoaded) {
                return;
            }

            if (loadingPromise) {
                return loadingPromise;
            }

            loadingPromise = (async () => {
                try {
                    console.log('[trading-view-wrapper] Loading Scripts');
                    console.log('[trading-view-wrapper] Loading charting-library');
                    await loadScript('/charting_library/charting_library/charting_library.js');

                    console.log('[trading-view-wrapper] Loading datafeeds');
                    await loadScript('/charting_library/datafeeds/udf/dist/bundle.js');

                    // Load CSS file
                    loadCSS('/charting_library/themed.css');

                    scriptsLoaded = true;
                    console.log('[trading-view-wrapper] Scripts loaded successfully');
                } catch (error) {
                    console.error('[trading-view-wrapper] Error loading scripts:', error);
                    throw error;
                }
            })();

            return loadingPromise;
        };

        const initWidget = async () => {
            try {
                if (!isMounted) return;

                await loadScripts();

                if (!isMounted || !containerRef.current) return;

                // Wait a bit for scripts to be fully loaded
                await new Promise(resolve => setTimeout(resolve, 100));

                // Initialize the TradingView widget
                if (typeof window !== 'undefined' && (window as any).TradingView) {
                    widget = new (window as any).TradingView.widget({
                        container: containerRef.current,
                        symbol: symbol, // Default symbol
                        interval: '1D',
                        theme: 'light',
                        style: '1',
                        locale: 'en',
                        toolbar_bg: '#f1f3f6',
                        enable_publishing: false,
                        allow_symbol_change: true,
                        container_id: 'tradingview_widget',
                        width: '100%',
                        height: '100%',
                        fullscreen: false,
                        // Configure the correct bundle path
                        library_path: '/charting_library/charting_library/',
                        // Load custom CSS
                        custom_css_url: '/charting_library/themed.css',
                        datafeed: Datafeed
                    });

                    console.log('[trading-view-wrapper] Widget Initialized successfully');
                    if (isMounted) {
                        setIsLoading(false);
                    }
                } else {
                    throw new Error('TradingView library not available');
                }
            } catch (error) {
                console.error('Error occurred while initializing tv widget: ', error);
                if (isMounted) {
                    setError(error instanceof Error ? error.message : 'Failed to initialize widget');
                    setIsLoading(false);
                }
            }
        };

        initWidget();

        // Cleanup function
        return () => {
            isMounted = false;
            if (widget && typeof widget.remove === 'function') {
                widget.remove();
            }
        };
    }, []); // Empty dependency array to run only once

    if (error) {
        return (
            <div style={{
                width: '100%',
                height: '100%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                backgroundColor: '#000'
            }}>
                <div style={{ color: 'red', textAlign: 'center' }}>
                    <h3>Error loading TradingView widget</h3>
                    <p>{error}</p>
                </div>
            </div>
        );
    }

    return (
        <div style={{
            width: '100%',
            height: '100%',
            position: 'relative',
            backgroundColor: '#000'
        }}>
            <div ref={containerRef} style={{ width: '100%', height: '100%' }}></div>
        </div>
    );
};

export default TradingViewWrapper;
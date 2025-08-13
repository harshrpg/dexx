// TradingView Widget Types
export interface TradingViewWidgetOptions {
    container: HTMLElement;
    locale?: string;
    library_path?: string;
    datafeed: any;
    symbol?: string;
    interval?: string;
    fullscreen?: boolean;
    debug?: boolean;
    width?: number | string;
    height?: number | string;
    theme?: 'light' | 'dark';
    timezone?: string;
    toolbar_bg?: string;
    enable_publishing?: boolean;
    hide_top_toolbar?: boolean;
    hide_legend?: boolean;
    save_image?: boolean;
    backgroundColor?: string;
    gridColor?: string;
    widthRatio?: number;
    heightRatio?: number;
    studies_overrides?: any;
    loading_screen?: any;
    custom_css_url?: string;
}

// Global declarations
declare global {
    interface Window {
        TradingView: {
            widget: new (options: TradingViewWidgetOptions) => any;
        };
        Datafeeds: {
            UDFCompatibleDatafeed: new (url: string) => any;
        };
    }
} 
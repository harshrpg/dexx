# TradingView Chart Integration

This document explains how to integrate TradingView charts into your Next.js TypeScript application.

## Overview

The TradingView integration provides React components that allow you to display professional trading charts in your application:

1. **`TradingViewWrapper`** - Safe wrapper for basic chart component (prevents hydration issues)
2. **`TradingViewThemedWrapper`** - Safe wrapper for themed chart component (prevents hydration issues)
3. **`TradingViewChart`** - Basic chart component with manual theme control (use wrapper instead)
4. **`TradingViewChartWithTheme`** - Advanced component that auto-adapts to your app's theme (use wrapper instead)

## Setup

### 1. Package Configuration

The `package.json` has been configured with the necessary scripts to copy TradingView files:

```json
{
  "scripts": {
    "postinstall": "npm run copy-files",
    "copy-files": "cp -R node_modules/charting_library/ public"
  },
  "dependencies": {
    "charting_library": "git@github.com:tradingview/charting_library.git"
  }
}
```

### 2. File Structure

After installation, the TradingView files will be available in:
- `/public/charting_library/` - Main charting library
- `/public/charting_library/datafeeds/udf/dist/bundle.js` - Data feed implementation

## Components

### TradingViewWrapper (Recommended)

Safe wrapper component that prevents hydration mismatches. Use this for basic charts.

```tsx
import TradingViewWrapper from '@/components/trading-view-wrapper';

<TradingViewWrapper 
  symbol="AAPL"
  interval="1D"
  theme="light"
  height={500}
  debug={false}
/>
```

#### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `symbol` | `string` | `'AAPL'` | Trading symbol to display |
| `interval` | `string` | `'1D'` | Chart time interval |
| `theme` | `'light' \| 'dark'` | `'light'` | Chart theme |
| `width` | `number \| string` | `'100%'` | Chart width |
| `height` | `number \| string` | `'600'` | Chart height |
| `fullscreen` | `boolean` | `true` | Enable fullscreen mode |
| `debug` | `boolean` | `false` | Enable debug mode |
| `datafeedUrl` | `string` | `'https://demo-feed-data.tradingview.com'` | Data feed URL |

### TradingViewThemedWrapper (Recommended)

Safe wrapper component that prevents hydration mismatches and auto-adapts to your application's theme.

```tsx
import TradingViewThemedWrapper from '@/components/trading-view-themed-wrapper';

<TradingViewThemedWrapper 
  symbol="TSLA"
  interval="1W"
  height={500}
  showToolbar={true}
  showLegend={true}
/>
```

#### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `symbol` | `string` | `'AAPL'` | Trading symbol to display |
| `interval` | `string` | `'1D'` | Chart time interval |
| `width` | `number \| string` | `'100%'` | Chart width |
| `height` | `number \| string` | `'600'` | Chart height |
| `fullscreen` | `boolean` | `true` | Enable fullscreen mode |
| `debug` | `boolean` | `false` | Enable debug mode |
| `datafeedUrl` | `string` | `'https://demo-feed-data.tradingview.com'` | Data feed URL |
| `showToolbar` | `boolean` | `true` | Show chart toolbar |
| `showLegend` | `boolean` | `true` | Show chart legend |
| `enablePublishing` | `boolean` | `false` | Enable publishing features |
| `customStudies` | `object` | `{}` | Custom study overrides |
| `loadingScreen` | `object` | `{}` | Custom loading screen configuration |

## Usage Examples

### Basic Stock Chart

```tsx
<TradingViewWrapper 
  symbol="AAPL"
  interval="1D"
  theme="light"
  height={500}
/>
```

### Crypto Chart with Dark Theme

```tsx
<TradingViewWrapper 
  symbol="BTCUSD"
  interval="4H"
  theme="dark"
  height={400}
/>
```

### Auto-Themed Chart

```tsx
<TradingViewThemedWrapper 
  symbol="TSLA"
  interval="1W"
  height={500}
  showToolbar={true}
  showLegend={true}
/>
```

### Custom Configuration

```tsx
<TradingViewThemedWrapper 
  symbol="NVDA"
  interval="1D"
  height={500}
  showToolbar={true}
  showLegend={true}
  enablePublishing={false}
  customStudies={{
    "volume.volume.color.0": "#FF0000",
    "volume.volume.color.1": "#00FF00",
  }}
  loadingScreen={{
    backgroundColor: "#ffffff",
    foregroundColor: "#000000"
  }}
/>
```

## Available Intervals

- `1` - 1 minute
- `5` - 5 minutes
- `15` - 15 minutes
- `30` - 30 minutes
- `60` - 1 hour
- `1H` - 1 hour
- `4H` - 4 hours
- `1D` - 1 day
- `1W` - 1 week
- `1M` - 1 month

## Available Symbols

The demo data feed supports various symbols including:

### Stocks
- `AAPL` - Apple Inc.
- `MSFT` - Microsoft Corporation
- `GOOGL` - Alphabet Inc.
- `TSLA` - Tesla Inc.
- `NVDA` - NVIDIA Corporation

### Cryptocurrencies
- `BTCUSD` - Bitcoin
- `ETHUSD` - Ethereum
- `ADAUSD` - Cardano

### Forex
- `EURUSD` - Euro/US Dollar
- `GBPUSD` - British Pound/US Dollar
- `USDJPY` - US Dollar/Japanese Yen

## Custom Data Feed

To use your own data feed, replace the `datafeedUrl` prop with your UDF-compatible endpoint:

```tsx
<TradingViewWrapper 
  symbol="CUSTOM"
  datafeedUrl="https://your-data-feed.com"
  // ... other props
/>
```

## Styling

The components include basic styling with Tailwind CSS classes. You can customize the appearance by:

1. Modifying the component styles
2. Using the `custom_css_url` option (advanced)
3. Overriding CSS classes

## Error Handling

The components include error handling for:
- Script loading failures
- Widget initialization errors
- Missing container elements
- Hydration mismatches (prevented by wrapper components)

Check the browser console for detailed error messages.

## Performance Considerations

- Scripts are loaded dynamically and cached
- Widgets are properly cleaned up on unmount
- Multiple charts can be rendered simultaneously
- Consider lazy loading for charts not immediately visible
- Wrapper components prevent hydration mismatches

## Demo Page

Visit `/trading-view` to see all examples in action.

## Troubleshooting

### Chart Not Loading

1. Check that the charting library files are in `/public/charting_library/`
2. Verify the data feed URL is accessible
3. Check browser console for errors
4. Ensure the container element exists

### Hydration Mismatches

1. **Always use wrapper components** (`TradingViewWrapper` or `TradingViewThemedWrapper`)
2. The wrapper components prevent hydration issues by only rendering on the client
3. If you see hydration warnings, ensure you're using the wrapper components

### Theme Issues

1. For `TradingViewThemedWrapper`, ensure `next-themes` is properly configured
2. Check that the theme provider wraps your application
3. Verify the theme values are 'light' or 'dark'

### TypeScript Errors

1. Ensure the types file is properly imported
2. Check that the global declarations are available
3. Verify the component props match the interface

## License

The TradingView charting library is subject to TradingView's license terms. Please review their licensing requirements for commercial use. 
'use client';

import dynamic from 'next/dynamic';
import Head from 'next/head';


const TradingViewWrapper = dynamic(() => import('@/components/tv/trading-view-wrapper'), {
    ssr: false,
});

export default function TradingViewPage() {
    //     return (
    //         <div className="container mx-auto p-6 space-y-8">
    //             <div className="text-center">
    //                 <h1 className="text-4xl font-bold mb-4">TradingView Chart Integration</h1>
    //                 <p className="text-lg text-gray-600 dark:text-gray-400">
    //                     Examples of TradingView charts integrated into Next.js with TypeScript
    //                 </p>
    //             </div>

    //             {/* Basic Chart Example */}
    //             <div className="space-y-4">
    //                 <h2 className="text-2xl font-semibold">Basic Chart (AAPL)</h2>
    //                 <div className="border rounded-lg p-4 bg-white dark:bg-gray-800">
    //                     <TradingViewWrapper
    //                         symbol="AAPL"
    //                         interval="1D"
    //                         theme="light"
    //                         height={500}
    //                         debug={false}
    //                     />
    //                 </div>
    //             </div>

    //             {/* Themed Chart Example */}
    //             {/* <div className="space-y-4">
    //                 <h2 className="text-2xl font-semibold">Auto-Themed Chart (TSLA)</h2>
    //                 <p className="text-sm text-gray-600 dark:text-gray-400">
    //                     This chart automatically adapts to your system theme
    //                 </p>
    //                 <div className="border rounded-lg p-4 bg-white dark:bg-gray-800">
    //                     <TradingViewChartWithTheme
    //                         symbol="TSLA"
    //                         interval="1W"
    //                         height={500}
    //                         debug={false}
    //                         showToolbar={true}
    //                         showLegend={true}
    //                     />
    //                 </div>
    //             </div> */}

    //             {/* Crypto Chart Example */}
    //             {/* <div className="space-y-4">
    //                 <h2 className="text-2xl font-semibold">Crypto Chart (BTCUSD)</h2>
    //                 <div className="border rounded-lg p-4 bg-white dark:bg-gray-800">
    //                     <TradingViewChart
    //                         symbol="BTCUSD"
    //                         interval="4H"
    //                         theme="dark"
    //                         height={400}
    //                         debug={false}
    //                     />
    //                 </div>
    //             </div> */}

    //             {/* Multiple Charts Grid */}
    //             {/* <div className="space-y-4">
    //                 <h2 className="text-2xl font-semibold">Multiple Charts Grid</h2>
    //                 <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
    //                     <div className="border rounded-lg p-4 bg-white dark:bg-gray-800">
    //                         <h3 className="text-lg font-medium mb-2">MSFT</h3>
    //                         <TradingViewChart
    //                             symbol="MSFT"
    //                             interval="1D"
    //                             theme="light"
    //                             height={300}
    //                             debug={false}
    //                         />
    //                     </div>
    //                     <div className="border rounded-lg p-4 bg-white dark:bg-gray-800">
    //                         <h3 className="text-lg font-medium mb-2">GOOGL</h3>
    //                         <TradingViewChart
    //                             symbol="GOOGL"
    //                             interval="1D"
    //                             theme="light"
    //                             height={300}
    //                             debug={false}
    //                         />
    //                     </div>
    //                 </div>
    //             </div> */}

    //             {/* Custom Configuration Example */}
    //             {/* <div className="space-y-4">
    //                 <h2 className="text-2xl font-semibold">Custom Configuration</h2>
    //                 <p className="text-sm text-gray-600 dark:text-gray-400">
    //                     Chart with custom studies and loading screen
    //                 </p>
    //                 <div className="border rounded-lg p-4 bg-white dark:bg-gray-800">
    //                     <TradingViewChartWithTheme
    //                         symbol="NVDA"
    //                         interval="1D"
    //                         height={500}
    //                         debug={false}
    //                         showToolbar={true}
    //                         showLegend={true}
    //                         enablePublishing={false}
    //                         customStudies={{
    //                             "volume.volume.color.0": "#FF0000",
    //                             "volume.volume.color.1": "#00FF00",
    //                         }}
    //                         loadingScreen={{
    //                             backgroundColor: "#ffffff",
    //                             foregroundColor: "#000000"
    //                         }}
    //                     />
    //                 </div>
    //             </div> */}

    //             {/* Usage Instructions */}
    //             <div className="space-y-4">
    //                 <h2 className="text-2xl font-semibold">Usage Instructions</h2>
    //                 <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-6">
    //                     <h3 className="text-lg font-medium mb-4">Basic Usage</h3>
    //                     <pre className="bg-gray-100 dark:bg-gray-800 p-4 rounded text-sm overflow-x-auto">
    //                         {`import TradingViewWrapper from '@/components/trading-view-wrapper';

    // <TradingViewWrapper 
    //   symbol="AAPL"
    //   interval="1D"
    //   theme="light"
    //   height={500}
    // />`}
    //                     </pre>

    //                     <h3 className="text-lg font-medium mb-4 mt-6">Themed Usage</h3>
    //                     {/* <pre className="bg-gray-100 dark:bg-gray-800 p-4 rounded text-sm overflow-x-auto">
    //                         {`import TradingViewChartWithTheme from '@/components/trading-view-chart-with-theme';

    // <TradingViewChartWithTheme 
    //   symbol="TSLA"
    //   interval="1W"
    //   height={500}
    //   showToolbar={true}
    //   showLegend={true}
    // />`}
    //                     </pre> */}
    //                 </div>
    //             </div>
    //         </div>
    //     );
    return (
        <div className='p-0'>
            <TradingViewWrapper />
        </div>
    )

} 
let currentMarkdownReport = "";
let currentTicker = "";
let mainChartInstance = null;

// Hardcoded popular market symbols for predictive search
const POPULAR_SYMBOLS = [
    { symbol: "AAPL", name: "Apple Inc." },
    { symbol: "MSFT", name: "Microsoft Corp." },
    { symbol: "GOOGL", name: "Alphabet Inc." },
    { symbol: "AMZN", name: "Amazon.com Inc." },
    { symbol: "META", name: "Meta Platforms" },
    { symbol: "TSLA", name: "Tesla Inc." },
    { symbol: "NVDA", name: "NVIDIA Corp." },
    { symbol: "JPM", name: "JPMorgan Chase" },
    { symbol: "V", name: "Visa Inc." },
    { symbol: "WMT", name: "Walmart Inc." }
];

document.addEventListener('DOMContentLoaded', () => {
    
    const tickerInput = document.getElementById('ticker');
    const searchDropdown = document.getElementById('search-dropdown');
    const runForm = document.getElementById('run-form');
    const spotlightContainer = document.getElementById('spotlight-container');
    const dashboardLayout = document.getElementById('dashboard-layout');
    const loadingState = document.getElementById('loading-state');
    
    // Auto-focus the Spotlight search
    if(tickerInput) {
        tickerInput.focus();
    }

    // New Search Button
    document.getElementById('new-search-btn')?.addEventListener('click', () => {
        dashboardLayout.classList.add('hidden');
        spotlightContainer.classList.remove('hidden');
        tickerInput.value = '';
        tickerInput.focus();
    });

    // Predictive Search Logic
    if (tickerInput) {
        tickerInput.addEventListener('input', (e) => {
            const query = e.target.value.toUpperCase();
            searchDropdown.innerHTML = '';
            
            if (query.length < 1) {
                searchDropdown.classList.add('hidden');
                return;
            }

            const matches = POPULAR_SYMBOLS.filter(item => 
                item.symbol.includes(query) || item.name.toUpperCase().includes(query)
            );

            if (matches.length > 0) {
                searchDropdown.classList.remove('hidden');
                matches.forEach(match => {
                    const div = document.createElement('div');
                    div.className = 'search-item';
                    div.innerHTML = `<span class="search-symbol">${match.symbol}</span><span class="search-name">${match.name}</span>`;
                    div.onclick = () => {
                        tickerInput.value = match.symbol;
                        searchDropdown.classList.add('hidden');
                    };
                    searchDropdown.appendChild(div);
                });
            } else {
                searchDropdown.classList.add('hidden');
            }
        });
    }

    document.addEventListener('click', (e) => {
        if (tickerInput && searchDropdown && !tickerInput.contains(e.target) && !searchDropdown.contains(e.target)) {
            searchDropdown.classList.add('hidden');
        }
    });

    if (runForm) {
        runForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            currentTicker = document.getElementById('ticker').value.toUpperCase();
            const months = document.getElementById('months').value;
            
            // Hide Spotlight, show loader
            spotlightContainer.classList.add('hidden');
            loadingState.classList.remove('hidden');
            searchDropdown.classList.add('hidden');
            
            try {
                // Append timestamp to bust cache and force fresh payload
                const response = await fetch(`/api/run?ticker=${currentTicker}&months=${months}&_t=${Date.now()}`);
                const result = await response.json();
                
                if (response.ok) {
                    loadingState.classList.add('hidden');
                    dashboardLayout.classList.remove('hidden');
                    document.getElementById('current-ticker-display').innerText = currentTicker;
                    
                    updateDashboard(result);
                } else {
                    alert(`Error: ${result.error}`);
                    loadingState.classList.add('hidden');
                    spotlightContainer.classList.remove('hidden');
                }
            } catch (error) {
                alert(`Error connecting to AI pipeline: ${error.message}`);
                loadingState.classList.add('hidden');
                spotlightContainer.classList.remove('hidden');
            }
        });
    }

    function updateDashboard(result) {
        const data = result.data;
        const closePrices = data.close;
        const currentPrice = closePrices[closePrices.length - 1];
        
        // 1. Update Metrics
        document.getElementById('current-price').innerText = `$${currentPrice.toFixed(2)}`;
        
        // Update Target Price
        const targetElement = document.getElementById('target-price');
        let targetVal = result.forecast.point[result.forecast.point.length - 1];
        if (!targetVal) {
             targetVal = currentPrice * 1.05;
        }
        targetElement.innerText = `$${targetVal.toFixed(2)}`;

        // Calculate and format risk metrics
        const maxDrawdown = (result.risk.metrics.max_drawdown_pct).toFixed(2);
        document.getElementById('max-drawdown').innerText = `${maxDrawdown}%`;
        
        const var95 = (result.risk.metrics.var_95_historical).toFixed(2);
        document.getElementById('var-95').innerText = `${var95}%`;
        
        // 2. Animate Gauges
        const volGauge = document.getElementById('volatility-gauge');
        const volVal = document.getElementById('volatility-val');
        const volPercent = Math.min(Math.round(result.risk.metrics.annualized_volatility_pct), 100);
        
        // Stroke dasharray for 36x36 svg circle is ~100
        if (volGauge) {
            volGauge.style.strokeDasharray = `${volPercent}, 100`;
        }
        if (volVal) {
            volVal.innerText = `${volPercent}%`;
        }

        const sharpeGauge = document.getElementById('sharpe-gauge');
        const sharpeVal = document.getElementById('sharpe-val');
        const sharpeRatio = result.risk.metrics.sharpe_ratio || 0;
        const sharpePercent = Math.min(Math.max(Math.round((sharpeRatio / 3) * 100), 0), 100);
        
        if (sharpeGauge) {
            sharpeGauge.style.strokeDasharray = `${sharpePercent}, 100`;
        }
        if (sharpeVal) {
            sharpeVal.innerText = sharpeRatio.toFixed(2);
        }

        // 3. Update Anomalies
        const anomalyList = document.getElementById('anomaly-list');
        const anomalyCount = document.getElementById('anomaly-count');
        anomalyList.innerHTML = '';
        
        if (result.anomalies.found && result.anomalies.anomalies.length > 0) {
            if (anomalyCount) anomalyCount.innerText = result.anomalies.anomalies.length;
            result.anomalies.anomalies.forEach(anomaly => {
                const li = document.createElement('li');
                li.className = 'anomaly-item';
                li.innerHTML = `
                    <div class="anomaly-icon"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg></div>
                    <div class="anomaly-content">
                        <span class="anomaly-title">${anomaly.kind || 'Deviation Detected'}</span>
                        <span class="anomaly-date">${anomaly.date || 'Recent'} - ${anomaly.severity || 'Medium'}</span>
                    </div>
                `;
                anomalyList.appendChild(li);
            });
        } else {
            if (anomalyCount) anomalyCount.innerText = '0';
            anomalyList.innerHTML = `
                <li class="anomaly-item" style="border-left-color: rgba(255,255,255,0.1);">
                    <span style="color: var(--text-muted); font-size: 0.8rem;">No critical anomalies detected in the selected timeframe.</span>
                </li>
            `;
        }

        // 4. Render Markdown Report directly to UI
        if (result.report && result.report.summary) {
            currentMarkdownReport = result.report.summary;
            const contentDiv = document.getElementById('report-content');
            if (contentDiv) {
                // Remove the image reference from the markdown since we already have the live chart in the UI
                let cleanMarkdown = currentMarkdownReport.replace(/!\[.*?\]\(.*?\)/g, '');
                contentDiv.innerHTML = marked.parse(cleanMarkdown);
            }
        }
        
        // 5. Render Chart
        renderChart(result);
    }
    
    function renderChart(result) {
        if (!result.data || !result.data.dates) return;
        
        const dates = result.data.dates;
        const o = result.data.open;
        const h = result.data.high;
        const l = result.data.low;
        const c = result.data.close;
        
        // Map into Lightweight Charts format {time, open, high, low, close}
        const ohlcData = dates.map((dt, i) => {
            let timestamp;
            if (dt.includes('day-')) {
                // Synthetic date: fake it by subtracting days from today
                let d = new Date();
                d.setDate(d.getDate() - (dates.length - i));
                timestamp = Math.floor(d.getTime() / 1000);
            } else {
                // 'YYYY-MM-DD' format works natively
                timestamp = dt;
            }
            return {
                time: timestamp,
                open: o[i],
                high: h[i],
                low: l[i],
                close: c[i]
            };
        });
        
        // Ensure data is sorted by time just in case
        ohlcData.sort((a, b) => {
            const timeA = typeof a.time === 'string' ? new Date(a.time).getTime() : a.time;
            const timeB = typeof b.time === 'string' ? new Date(b.time).getTime() : b.time;
            return timeA - timeB;
        });
        
        // Forecast Data
        const forecastLength = result.forecast.point.length;
        const lastCandle = ohlcData[ohlcData.length - 1];
        
        const forecastData = [];
        forecastData.push({ time: lastCandle.time, value: lastCandle.close });
        
        let lastDateVal;
        if (typeof lastCandle.time === 'string') {
            lastDateVal = new Date(lastCandle.time);
        } else {
            lastDateVal = new Date(lastCandle.time * 1000);
        }

        for (let i = 0; i < forecastLength; i++) {
            lastDateVal.setDate(lastDateVal.getDate() + 1);
            // Skip weekends to align with business days (simple heuristic for charts)
            if (lastDateVal.getDay() === 0) lastDateVal.setDate(lastDateVal.getDate() + 1);
            if (lastDateVal.getDay() === 6) lastDateVal.setDate(lastDateVal.getDate() + 2);
            
            let timeVal;
            if (typeof lastCandle.time === 'string') {
                timeVal = lastDateVal.toISOString().split('T')[0];
            } else {
                timeVal = Math.floor(lastDateVal.getTime() / 1000);
            }
            forecastData.push({
                time: timeVal,
                value: result.forecast.point[i]
            });
        }
        
        const container = document.querySelector('.chart-container');
        container.innerHTML = ''; // Clear previous canvas or charts
        
        // Create Lightweight Chart
        const chartOptions = { 
            layout: { 
                textColor: '#8b949e', 
                background: { type: 'solid', color: 'transparent' } 
            },
            grid: {
                vertLines: { color: 'rgba(255, 255, 255, 0.05)' },
                horzLines: { color: 'rgba(255, 255, 255, 0.05)' }
            },
            crosshair: {
                mode: 1 // Magnet mode
            },
            // The user requested native pan/zoom interactivity, which this library provides out of the box!
        };
        
        mainChartInstance = LightweightCharts.createChart(container, chartOptions);
        
        const candlestickSeries = mainChartInstance.addSeries(LightweightCharts.CandlestickSeries, {
            upColor: '#00f3ff',
            downColor: '#ff8a00',
            borderVisible: false,
            wickUpColor: '#00f3ff',
            wickDownColor: '#ff8a00'
        });
        candlestickSeries.setData(ohlcData);

        const forecastSeries = mainChartInstance.addSeries(LightweightCharts.LineSeries, {
            color: 'rgba(255, 138, 0, 0.9)',
            lineWidth: 2,
            lineStyle: 2, // Dashed
            crosshairMarkerVisible: false,
            lastValueVisible: false,
            priceLineVisible: false
        });
        forecastSeries.setData(forecastData);

        mainChartInstance.timeScale().fitContent();
        
        // Handle window resize dynamically since we attach to the container
        new ResizeObserver(entries => {
            if (entries.length === 0 || entries[0].target !== container) return;
            const newRect = entries[0].contentRect;
            mainChartInstance.applyOptions({ width: newRect.width, height: newRect.height });
        }).observe(container);
    }

    // PDF Export Logic
    const downloadBtn = document.getElementById('download-btn');
    if (downloadBtn) {
        downloadBtn.addEventListener('click', () => {
            if (!currentMarkdownReport) return;
            
            // Create a temporary container for a highly aesthetic PDF layout
            const printContainer = document.createElement('div');
            
            const dateStr = new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' });
            const tickerText = currentTicker ? currentTicker.toUpperCase() : 'ASSET';
            
            printContainer.innerHTML = `
                <style>
                    .pdf-export-wrapper {
                        padding: 40px;
                        background: #ffffff;
                        color: #1a1a2e;
                        font-family: 'Inter', -apple-system, sans-serif;
                        line-height: 1.6;
                    }
                    .pdf-header {
                        border-bottom: 3px solid #00f3ff;
                        padding-bottom: 15px;
                        margin-bottom: 30px;
                        display: flex;
                        justify-content: space-between;
                        align-items: flex-end;
                    }
                    .pdf-brand h1 {
                        color: #0B0E14;
                        font-size: 28px;
                        margin: 0;
                        font-weight: 800;
                        letter-spacing: -0.5px;
                    }
                    .pdf-brand h2 {
                        color: #ff8a00;
                        font-size: 14px;
                        margin: 5px 0 0 0;
                        font-weight: 600;
                        text-transform: uppercase;
                        letter-spacing: 1px;
                    }
                    .pdf-meta {
                        text-align: right;
                        color: #64748b;
                        font-size: 12px;
                    }
                    .pdf-meta strong {
                        color: #0B0E14;
                        font-size: 18px;
                        display: block;
                    }
                    .pdf-content h2 {
                        color: #0B0E14;
                        font-size: 20px;
                        margin-top: 30px;
                        margin-bottom: 15px;
                        padding-bottom: 5px;
                        border-bottom: 1px solid #e2e8f0;
                    }
                    .pdf-content h3 {
                        color: #0070f3;
                        font-size: 16px;
                        margin-top: 20px;
                        margin-bottom: 10px;
                    }
                    .pdf-content h4 {
                        font-size: 14px;
                        color: #334155;
                    }
                    .pdf-content p, .pdf-content li {
                        font-size: 13.5px;
                        color: #334155;
                    }
                    .pdf-content table {
                        width: 100%;
                        border-collapse: collapse;
                        margin: 20px 0;
                        font-size: 13px;
                    }
                    .pdf-content th {
                        background: #f1f5f9;
                        color: #0f172a;
                        font-weight: 600;
                        text-align: left;
                        padding: 10px;
                        border-bottom: 2px solid #cbd5e1;
                    }
                    .pdf-content td {
                        padding: 10px;
                        border-bottom: 1px solid #e2e8f0;
                        color: #334155;
                    }
                    .pdf-content tr:nth-child(even) {
                        background: #f8fafc;
                    }
                    .pdf-content blockquote {
                        margin: 20px 0;
                        padding: 15px 20px;
                        background: #fff8f1;
                        border-left: 4px solid #ff8a00;
                        color: #9a3412;
                        font-style: italic;
                    }
                    .pdf-footer {
                        margin-top: 50px;
                        padding-top: 20px;
                        border-top: 1px solid #e2e8f0;
                        text-align: center;
                        font-size: 10px;
                        color: #94a3b8;
                    }
                </style>
                <div class="pdf-export-wrapper">
                    <div class="pdf-header">
                        <div class="pdf-brand">
                            <h1>Insight Engine</h1>
                            <h2>Quantitative AI Synthesis</h2>
                        </div>
                        <div class="pdf-meta">
                            <strong>${tickerText}</strong>
                            <span>Generated: ${dateStr}</span>
                        </div>
                    </div>
                    <div class="pdf-content">
                        ${marked.parse(currentMarkdownReport)}
                    </div>
                    <div class="pdf-footer">
                        STRICTLY CONFIDENTIAL • AI-Generated Analysis • Not Financial Advice
                    </div>
                </div>
            `;
            document.body.appendChild(printContainer);
            
            const overlay = document.createElement('div');
            overlay.style.position = 'fixed';
            overlay.style.top = '0';
            overlay.style.left = '0';
            overlay.style.width = '100vw';
            overlay.style.height = '100vh';
            overlay.style.backgroundColor = '#0B0E14';
            overlay.style.zIndex = '9999';
            overlay.style.display = 'flex';
            overlay.style.flexDirection = 'column';
            overlay.style.alignItems = 'center';
            overlay.style.justifyContent = 'center';
            overlay.innerHTML = '<div class="spinner"></div><p style="margin-top: 1rem; color: #e2e8f0;">Generating PDF Document...</p>';
            document.body.appendChild(overlay);
            
            const opt = {
                margin:       0.5,
                filename:     `${currentTicker || 'analysis'}_report.pdf`,
                image:        { type: 'jpeg', quality: 0.98 },
                html2canvas:  { scale: 2, useCORS: true },
                jsPDF:        { unit: 'in', format: 'letter', orientation: 'portrait' } // Switched to portrait for document text
            };
            
            setTimeout(() => {
                html2pdf().set(opt).from(printContainer).save().then(() => {
                    document.body.removeChild(printContainer);
                    document.body.removeChild(overlay);
                });
            }, 300);
        });
    }

    // Markdown Export Logic
    const downloadMdBtn = document.getElementById('download-md-btn');
    if (downloadMdBtn) {
        downloadMdBtn.addEventListener('click', () => {
            if (!currentMarkdownReport) return;
            
            const blob = new Blob([currentMarkdownReport], { type: 'text/markdown' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${currentTicker || 'analysis'}_report.md`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        });
    }
});

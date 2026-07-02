let currentMarkdownReport = "";
let currentTicker = "";
let mainChartInstance = null;
let volumeChartInstance = null;

// Drawing & Zoom State
let drawMode = 'pointer'; // 'pointer' or 'line'
let isDrawing = false;
let startXVal = null;
let startYVal = null;
let currentLineId = null;
let annotationColor = '#00f3ff';
let chartAnnotations = {};

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
    { symbol: "JNJ", name: "Johnson & Johnson" },
    { symbol: "WMT", name: "Walmart Inc." },
    { symbol: "PG", name: "Procter & Gamble" },
    { symbol: "MA", name: "Mastercard Inc." },
    { symbol: "UNH", name: "UnitedHealth Group" },
    { symbol: "HD", name: "Home Depot" },
    { symbol: "BAC", name: "Bank of America" },
    { symbol: "DIS", name: "Walt Disney Co." },
    { symbol: "NFLX", name: "Netflix Inc." },
    { symbol: "BTC-USD", name: "Bitcoin" },
    { symbol: "ETH-USD", name: "Ethereum" },
    { symbol: "SPY", name: "S&P 500 ETF" },
    { symbol: "QQQ", name: "Invesco QQQ Trust" }
];

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('run-form');
    const submitBtn = document.getElementById('submit-btn');
    const loadingState = document.getElementById('loading-state');
    const dashboardGrid = document.getElementById('dashboard-grid');
    const exportPanel = document.getElementById('export-panel');
    const reportContent = document.getElementById('report-content');
    
    // Sidebar Navigation Logic
    const navOverview = document.getElementById('nav-overview');
    const navChart = document.getElementById('nav-chart');
    const navRisk = document.getElementById('nav-risk');
    
    function switchView(viewName, activeNav) {
        // Reset nav states
        [navOverview, navChart, navRisk].forEach(nav => nav && nav.classList.remove('active'));
        if (activeNav) activeNav.classList.add('active');
        
        // Reset grid views
        dashboardGrid.classList.remove('view-chart', 'view-risk');
        
        if (viewName === 'chart') {
            dashboardGrid.classList.add('view-chart');
        } else if (viewName === 'risk') {
            dashboardGrid.classList.add('view-risk');
        }
    }

    if (navOverview) navOverview.addEventListener('click', () => switchView('overview', navOverview));
    if (navChart) navChart.addEventListener('click', () => switchView('chart', navChart));
    if (navRisk) navRisk.addEventListener('click', () => switchView('risk', navRisk));

    // Settings Modal Logic
    const settingsBtn = document.getElementById('top-settings');
    const settingsModal = document.getElementById('settings-modal');
    const closeModal = document.getElementById('close-modal');
    
    if (settingsBtn && settingsModal) {
        settingsBtn.addEventListener('click', () => settingsModal.classList.remove('hidden'));
        closeModal.addEventListener('click', () => settingsModal.classList.add('hidden'));
        settingsModal.addEventListener('click', (e) => {
            if (e.target === settingsModal) settingsModal.classList.add('hidden');
        });
    }

    // Predictive Search Logic
    const tickerInput = document.getElementById('ticker');
    const searchDropdown = document.getElementById('search-dropdown');

    if (tickerInput && searchDropdown) {
        tickerInput.addEventListener('input', (e) => {
            const query = e.target.value.toLowerCase().trim();
            searchDropdown.innerHTML = '';
            
            if (query.length === 0) {
                searchDropdown.classList.add('hidden');
                return;
            }

            const matches = POPULAR_SYMBOLS.filter(s => 
                s.symbol.toLowerCase().includes(query) || 
                s.name.toLowerCase().includes(query)
            ).slice(0, 5); // show top 5

            if (matches.length > 0) {
                searchDropdown.classList.remove('hidden');
                matches.forEach(match => {
                    const div = document.createElement('div');
                    div.className = 'search-item';
                    div.innerHTML = `<span class="search-symbol">${match.symbol}</span><span class="search-name">${match.name}</span>`;
                    div.addEventListener('click', () => {
                        tickerInput.value = match.symbol;
                        searchDropdown.classList.add('hidden');
                    });
                    searchDropdown.appendChild(div);
                });
            } else {
                searchDropdown.classList.add('hidden');
            }
        });

        // Hide dropdown when clicking outside
        document.addEventListener('click', (e) => {
            if (!tickerInput.contains(e.target) && !searchDropdown.contains(e.target)) {
                searchDropdown.classList.add('hidden');
            }
        });
    }

    // Set default Chart.js settings for the Sci-Fi theme
    Chart.defaults.color = '#8b949e';
    Chart.defaults.font.family = "'Inter', sans-serif";
    Chart.defaults.plugins.tooltip.backgroundColor = 'rgba(0,0,0,0.8)';
    Chart.defaults.plugins.tooltip.titleColor = '#00f3ff';

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // Hide results and show loading
        dashboardGrid.classList.add('hidden');
        exportPanel.classList.add('hidden');
        loadingState.classList.remove('hidden');
        submitBtn.disabled = true;
        submitBtn.innerText = "Synthesizing...";
        submitBtn.style.opacity = '0.5';
        
        // System status pulsing
        const topStatus = document.getElementById('top-status');
        if (topStatus) {
            topStatus.classList.remove('status-active');
            topStatus.classList.add('status-pulsing');
        }
        
        const ticker = document.getElementById('ticker').value.toUpperCase();
        const months = document.getElementById('months').value;

        try {
            const timestamp = new Date().getTime();
            const params = new URLSearchParams({
                ticker: ticker,
                months: months,
                _t: timestamp // cache buster
            });

            const response = await fetch(`/api/run?${params.toString()}`);
            if (!response.ok) throw new Error('Pipeline execution failed');

            const result = await response.json();
            
            // Wait for charts to be generated and saved, then fetch the image for PDF
            const chartTimestamp = new Date().getTime(); 
            const chartImg = document.getElementById('chart-image');
            chartImg.src = `/artifacts/charts/${ticker}_chart.png?t=${chartTimestamp}`;
            
            renderDashboard(result, ticker);
            renderExportPanel(result, ticker);

        } catch (error) {
            console.error(error);
            alert(`Error: ${error.message}`);
        } finally {
            submitBtn.disabled = false;
            submitBtn.innerText = "Run Analysis";
            submitBtn.style.opacity = '1';
            loadingState.classList.add('hidden');
            
            // Set status to green
            const topStatus = document.getElementById('top-status');
            if (topStatus) {
                topStatus.classList.remove('status-pulsing');
                topStatus.classList.add('status-active');
            }
        }
    });

    function renderDashboard(result, ticker) {
        dashboardGrid.classList.remove('hidden');
        
        const closePrices = result.data.close;
        const volume = result.data.volume;
        const currentPrice = closePrices[closePrices.length - 1];
        
        const forecastPoint = result.forecast.point;
        const targetPrice = forecastPoint[forecastPoint.length - 1];
        
        // Render Bottom Metrics
        document.getElementById('val-current-price').innerText = currentPrice.toFixed(2);
        document.getElementById('val-target-price').innerText = targetPrice.toFixed(2);
        
        // Render Risk Metrics
        const metrics = result.risk.metrics;
        document.getElementById('val-volatility').innerText = metrics.annualized_volatility_pct ? metrics.annualized_volatility_pct + '%' : 'N/A';
        document.getElementById('val-drawdown').innerText = metrics.max_drawdown_pct ? metrics.max_drawdown_pct + '%' : 'N/A';
        document.getElementById('val-var95').innerText = metrics.var_95_pct ? metrics.var_95_pct + '%' : 'N/A';
        document.getElementById('val-var99').innerText = metrics.var_99_pct ? metrics.var_99_pct + '%' : 'N/A';
        
        // Update Gauges
        // Sharpe usually between -1 and 3. Map to 0-100 for gauge.
        let sharpe = metrics.sharpe_ratio || 0;
        let sharpeGaugeVal = Math.min(Math.max((sharpe + 1) * 25, 0), 100); 
        updateSVGOffset('gauge-risk', sharpeGaugeVal);
        document.getElementById('val-sharpe').innerText = sharpe.toFixed(2);
        
        // Confidence usually High/Medium/Low, or percentage. Let's map Critique confidence
        let confidenceStr = result.critique.confidence || "Unknown";
        let confScore = 50;
        if (confidenceStr.toLowerCase() === 'high') confScore = 90;
        if (confidenceStr.toLowerCase() === 'medium') confScore = 60;
        if (confidenceStr.toLowerCase() === 'low') confScore = 30;
        updateSVGOffset('gauge-score', confScore);
        document.getElementById('val-confidence').innerText = confidenceStr;

        // Render Anomalies
        const anomalyList = document.getElementById('anomaly-list');
        const alertBadge = document.getElementById('alert-badge');
        anomalyList.innerHTML = '';
        if (result.anomalies.found && result.anomalies.anomalies.length > 0) {
            if (alertBadge) alertBadge.classList.remove('hidden');
            
            result.anomalies.anomalies.forEach(a => {
                const li = document.createElement('li');
                li.className = 'anomaly-item';
                li.innerHTML = `
                    <div class="anomaly-icon"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg></div>
                    <div class="anomaly-content">
                        <span class="anomaly-title">${a.kind}</span>
                        <span class="anomaly-date">${a.date} - ${a.severity}</span>
                    </div>
                `;
                anomalyList.appendChild(li);
            });
        } else {
            if (alertBadge) alertBadge.classList.add('hidden');
            anomalyList.innerHTML = `<li style="color: var(--neon-cyan); padding: 1rem; text-align: center;">System Nominal. No statistical anomalies detected.</li>`;
        }

        // Render Chart.js
        renderCharts(result);
    }

    function updateSVGOffset(id, percentage) {
        // Total dasharray length for the half-circle is ~125.6
        // offset 125.6 = empty, offset 0 = full
        const path = document.getElementById(id);
        if(path) {
            const offset = 125.6 - (percentage / 100 * 125.6);
            path.style.strokeDashoffset = offset;
        }
    }

    function renderCharts(result) {
        const histClose = result.data.close;
        const forecastPoint = result.forecast.point;
        
        // Prepare Candlestick data
        const candlestickData = histClose.map((c, i) => {
            let dateStr = result.data.dates[i];
            let timestamp;
            if (dateStr.includes('day-')) {
                // Synthetic date: map index to past days
                timestamp = luxon.DateTime.now().minus({ days: histClose.length - i }).valueOf();
            } else {
                // Live ISO date
                timestamp = luxon.DateTime.fromISO(dateStr).valueOf();
            }
            return {
                x: timestamp,
                o: result.data.open[i],
                h: result.data.high[i],
                l: result.data.low[i],
                c: c
            };
        });

        // Prepare Forecast data (connect to last historical point)
        const lastTimestamp = candlestickData[candlestickData.length - 1].x;
        const forecastData = [];
        forecastData.push({ x: lastTimestamp, y: histClose[histClose.length - 1] });
        
        for(let i=0; i<forecastPoint.length; i++) {
            forecastData.push({
                x: lastTimestamp + (i + 1) * 86400000, // add 1 day in ms
                y: forecastPoint[i]
            });
        }

        // Main Chart (Candlestick + Forecast Line)
        const ctxMain = document.getElementById('mainChart').getContext('2d');
        if (mainChartInstance) mainChartInstance.destroy();
        
        mainChartInstance = new Chart(ctxMain, {
            type: 'candlestick',
            data: {
                datasets: [
                    {
                        label: 'Historical',
                        data: candlestickData,
                        color: {
                            up: 'rgba(0, 243, 255, 0.8)',
                            down: 'rgba(255, 138, 0, 0.8)',
                            unchanged: 'rgba(153, 153, 153, 0.8)'
                        },
                        borderColor: {
                            up: '#00f3ff',
                            down: '#ff8a00',
                            unchanged: '#999'
                        },
                        borderWidth: 1.5
                    },
                    {
                        type: 'line',
                        label: 'Forecast',
                        data: forecastData,
                        borderColor: '#ff8a00',
                        borderDash: [5, 5],
                        borderWidth: 2,
                        fill: false,
                        pointRadius: 0,
                        pointHoverRadius: 4,
                        tension: 0.1
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: { 
                        type: 'time',
                        time: { unit: 'day' },
                        display: false 
                    },
                    y: { 
                        grid: { color: 'rgba(255,255,255,0.05)' },
                        border: { display: false }
                    }
                },
                plugins: {
                    legend: { display: false },
                    annotation: {
                        annotations: chartAnnotations
                    },
                    zoom: {
                        pan: {
                            enabled: true,
                            mode: 'x'
                        },
                        zoom: {
                            wheel: { enabled: false }, // disabled scroll zoom
                            pinch: { enabled: true },
                            mode: 'x'
                        }
                    }
                }
            }
        });

        // Initialize Zoom Buttons
        document.getElementById('zoom-in-btn').onclick = () => mainChartInstance.zoom(1.1);
        document.getElementById('zoom-out-btn').onclick = () => mainChartInstance.zoom(0.9);

        // Initialize Drawing Toolbar
        const btnPointer = document.getElementById('tool-pointer');
        const btnLine = document.getElementById('tool-line');
        const btnClear = document.getElementById('tool-clear');
        const colorPicker = document.getElementById('tool-color');

        const updateToolState = (mode) => {
            drawMode = mode;
            btnPointer.classList.toggle('active', mode === 'pointer');
            btnLine.classList.toggle('active', mode === 'line');
            mainChartInstance.options.plugins.zoom.pan.enabled = (mode === 'pointer');
            mainChartInstance.update('none');
        };

        btnPointer.onclick = () => updateToolState('pointer');
        btnLine.onclick = () => updateToolState('line');
        btnClear.onclick = () => {
            chartAnnotations = {};
            mainChartInstance.options.plugins.annotation.annotations = chartAnnotations;
            mainChartInstance.update();
        };
        colorPicker.onchange = (e) => annotationColor = e.target.value;

        // Interactive Canvas Drawing Engine
        const canvas = document.getElementById('mainChart');
        
        canvas.onmousedown = (e) => {
            if (drawMode !== 'line') return;
            isDrawing = true;
            
            const rect = canvas.getBoundingClientRect();
            const xPixel = e.clientX - rect.left;
            const yPixel = e.clientY - rect.top;
            
            startXVal = mainChartInstance.scales.x.getValueForPixel(xPixel);
            startYVal = mainChartInstance.scales.y.getValueForPixel(yPixel);
            
            currentLineId = 'line_' + Date.now();
            chartAnnotations[currentLineId] = {
                type: 'line',
                xMin: startXVal,
                xMax: startXVal,
                yMin: startYVal,
                yMax: startYVal,
                borderColor: annotationColor,
                borderWidth: 2,
                borderDash: [5, 5] // dashed while drawing
            };
            mainChartInstance.update('none');
        };

        canvas.onmousemove = (e) => {
            if (!isDrawing || drawMode !== 'line') return;
            
            const rect = canvas.getBoundingClientRect();
            const xPixel = e.clientX - rect.left;
            const yPixel = e.clientY - rect.top;
            
            const curXVal = mainChartInstance.scales.x.getValueForPixel(xPixel);
            const curYVal = mainChartInstance.scales.y.getValueForPixel(yPixel);
            
            chartAnnotations[currentLineId].xMax = curXVal;
            chartAnnotations[currentLineId].yMax = curYVal;
            mainChartInstance.update('none');
        };

        canvas.onmouseup = () => {
            if (!isDrawing || drawMode !== 'line') return;
            isDrawing = false;
            // Solidify the line
            chartAnnotations[currentLineId].borderDash = [];
            mainChartInstance.update('none');
        };
        canvas.onmouseleave = canvas.onmouseup;

        // Volume Chart (Keep as Bar chart)
        const volCtx = document.getElementById('volumeChart').getContext('2d');
        if (volumeChartInstance) volumeChartInstance.destroy();
        
        const volLabels = result.data.volume.map((_, i) => i);
        // Color volume bars based on close vs open
        const volColors = result.data.volume.map((_, i) => {
            return result.data.close[i] >= result.data.open[i] ? 'rgba(0, 243, 255, 0.3)' : 'rgba(255, 138, 0, 0.3)';
        });
        
        volumeChartInstance = new Chart(volCtx, {
            type: 'bar',
            data: {
                labels: volLabels,
                datasets: [{
                    label: 'Volume',
                    data: result.data.volume,
                    backgroundColor: volColors,
                    borderRadius: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: { display: false },
                    y: { display: false }
                },
                plugins: { 
                    legend: { display: false },
                    zoom: {
                        pan: { enabled: true, mode: 'x' },
                        zoom: { wheel: { enabled: false }, pinch: { enabled: true }, mode: 'x' }
                    }
                }
            }
        });
    }

    function renderExportPanel(result, ticker) {
        exportPanel.classList.remove('hidden');
        
        if (result.report && result.report.markdown) {
            currentMarkdownReport = result.report.markdown;
        } else if (result.report && result.report.summary) {
            currentMarkdownReport = result.report.summary;
        }
        
        currentTicker = ticker;
        reportContent.innerHTML = marked.parse(currentMarkdownReport);
    }

    // PDF and MD Export Logic
    const downloadBtn = document.getElementById('download-btn');
    if (downloadBtn) {
        downloadBtn.addEventListener('click', () => {
            if (!currentMarkdownReport) return;
            
            const element = document.getElementById('pdf-content');
            
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
            overlay.innerHTML = '<div class="spinner"></div><p style="margin-top: 1rem; color: #e2e8f0;">Generating Professional PDF...</p>';
            document.body.appendChild(overlay);

            element.classList.add('pdf-export-mode');
            const chartImage = document.getElementById('chart-image');
            if (chartImage) chartImage.classList.remove('hidden');
            
            const pdfHeader = document.createElement('div');
            pdfHeader.id = 'temp-pdf-header';
            pdfHeader.innerHTML = `
                <div style="text-align: center; margin-bottom: 2rem; padding-bottom: 1rem; border-bottom: 2px solid #000;">
                    <h1 style="font-size: 24pt; font-weight: bold; margin: 0; color: black;">Insight Engine</h1>
                    <p style="font-size: 12pt; color: #555; margin: 5px 0 0 0;">Autonomous Financial Forecasting & Anomaly Detection</p>
                </div>
            `;
            element.insertBefore(pdfHeader, element.firstChild);
            
            const extended = document.getElementById('pdf-extended-methodology');
            let wasExtendedHidden = false;
            if (extended && extended.style.display === 'none') {
                wasExtendedHidden = true;
                extended.style.display = 'block';
            }

            const opt = {
                margin:       0.5,
                filename:     `${currentTicker || 'analysis'}_report.pdf`,
                image:        { type: 'jpeg', quality: 0.98 },
                html2canvas:  { scale: 2, useCORS: true },
                jsPDF:        { unit: 'in', format: 'letter', orientation: 'portrait' }
            };
            
            setTimeout(() => {
                html2pdf().set(opt).from(element).save().then(() => {
                    element.classList.remove('pdf-export-mode');
                    const tempHeader = document.getElementById('temp-pdf-header');
                    if (tempHeader) tempHeader.remove();
                    if (wasExtendedHidden && extended) {
                        extended.style.display = 'none';
                    }
                    if (chartImage) chartImage.classList.add('hidden');
                    document.body.removeChild(overlay);
                });
            }, 300);
        });
    }

    const downloadMdBtn = document.getElementById('download-md-btn');
    if (downloadMdBtn) {
        downloadMdBtn.addEventListener('click', () => {
            if (!currentMarkdownReport) return;
            
            let fullMarkdown = `# Insight Engine Report\n*Autonomous Financial Forecasting & Anomaly Detection*\n\n---\n\n`;
            fullMarkdown += currentMarkdownReport;
            
            fullMarkdown += `\n\n---\n\n`;
            fullMarkdown += `## Deep Dive: Analytical Methodology\n\n`;
            fullMarkdown += `This report extends the executive summary with a comprehensive breakdown of the multi-agent orchestration pipeline and quantitative models used to evaluate the asset.\n\n`;
            fullMarkdown += `### 1. Data Ingestion & Integrity\n`;
            fullMarkdown += `The Insight Engine fetches high-fidelity Open, High, Low, Close, and Volume (OHLCV) data directly from live market feeds. To ensure data integrity, the pipeline employs fallback caching and strict type-checking at the boundary. The dataset spans the exact timeframe requested, capturing both macroeconomic drift and micro-level volatility.\n\n`;
            fullMarkdown += `### 2. Forecasting Engine: ARIMA + Prophet Ensemble\n`;
            fullMarkdown += `Our forecasting agent relies on a sophisticated ensemble method to project price action for the next 30 trading days.\n`;
            fullMarkdown += `- **ARIMA (Auto-Regressive Integrated Moving Average):** Captures the asset's momentum and mean-reversion characteristics by analyzing its own lagged values.\n`;
            fullMarkdown += `- **Prophet:** A robust additive model designed by Meta that excels at handling missing daily data and abrupt trend shifts.\n`;
            fullMarkdown += `- **Ensemble Synthesis:** By blending both models, we neutralize their individual weaknesses. The 95% Confidence Interval (CI) represents the statistical certainty boundary—a wider band indicates higher expected market turbulence.\n\n`;
            fullMarkdown += `### 3. Anomaly Detection Systems\n`;
            fullMarkdown += `Financial anomalies often precede massive market movements. We deploy three independent algorithms to flag them:\n`;
            fullMarkdown += `- **Isolation Forests:** An unsupervised machine learning algorithm that isolates outliers by randomly partitioning the dataset. Highly effective at detecting structural breaks in trading behavior.\n`;
            fullMarkdown += `- **Rolling Z-Scores:** We calculate a rolling standard deviation of daily volume. Any volume spike exceeding predefined Z-score thresholds triggers a severity alert, indicating institutional accumulation or distribution.\n`;
            fullMarkdown += `- **Bollinger Band Breaches:** We monitor price excursions beyond 2 standard deviations from the 20-day Simple Moving Average (SMA) to identify overbought or oversold exhaustion points.\n\n`;
            fullMarkdown += `### 4. Quantitative Risk Assessment\n`;
            fullMarkdown += `Raw returns are meaningless without risk context. The engine computes institutional-grade risk metrics:\n`;
            fullMarkdown += `- **Sharpe Ratio:** Calculates the risk-adjusted return. A ratio above 1.0 indicates excellent returns relative to the volatility endured.\n`;
            fullMarkdown += `- **Value at Risk (VaR):** Estimates the maximum expected loss over a set period at a 95% and 99% confidence level, providing a worst-case scenario floor.\n`;
            fullMarkdown += `- **Maximum Drawdown:** The largest historical peak-to-trough drop in the asset's price, serving as a historical stress test.\n\n`;
            fullMarkdown += `*Note: The Insight Engine autonomously critiques its own models and will flag warnings if the forecast confidence falls below acceptable thresholds.*\n`;
            
            const blob = new Blob([fullMarkdown], { type: 'text/markdown' });
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

    const readMoreBtn = document.getElementById('read-more-btn');
    const extendedMethodology = document.getElementById('pdf-extended-methodology');
    
    if (readMoreBtn && extendedMethodology) {
        readMoreBtn.addEventListener('click', () => {
            if (extendedMethodology.style.display === 'none') {
                extendedMethodology.style.display = 'block';
                readMoreBtn.innerHTML = '▲';
            } else {
                extendedMethodology.style.display = 'none';
                readMoreBtn.innerHTML = '•••';
            }
        });
    }
});

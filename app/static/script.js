document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('run-form');
    const submitBtn = document.getElementById('submit-btn');
    const loadingState = document.getElementById('loading-state');
    const resultsPanel = document.getElementById('results-panel');
    const reportContent = document.getElementById('report-content');
    const chartImage = document.getElementById('chart-image');
    
    let currentMarkdownReport = "";
    let currentTicker = "";

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // Hide results and show loading
        resultsPanel.classList.add('hidden');
        loadingState.classList.remove('hidden');
        submitBtn.disabled = true;
        submitBtn.style.opacity = '0.5';
        const ticker = document.getElementById('ticker').value.toUpperCase();
        const months = document.getElementById('months').value;

        try {
            // Build query params
            const params = new URLSearchParams({
                ticker: ticker,
                months: months
            });

            // Call the backend API
            const response = await fetch(`/api/run?${params.toString()}`);
            
            if (!response.ok) {
                throw new Error('Pipeline execution failed');
            }

            const result = await response.json();
            
            // Render the results
            renderResults(result, ticker);

        } catch (error) {
            console.error(error);
            alert(`Error: ${error.message}`);
        } finally {
            // Re-enable button
            submitBtn.disabled = false;
            submitBtn.style.opacity = '1';
            loadingState.classList.add('hidden');
        }
    });

    function renderResults(result, ticker) {
        // Show the panel
        resultsPanel.classList.remove('hidden');
        
        // Render Markdown Report
        if (result.report && result.report.markdown) {
            currentMarkdownReport = result.report.markdown;
            currentTicker = ticker;
            reportContent.innerHTML = marked.parse(result.report.markdown);
        } else if (result.report && result.report.summary) {
            currentMarkdownReport = result.report.summary;
            currentTicker = ticker;
            reportContent.innerHTML = marked.parse(result.report.summary);
        } else {
            currentMarkdownReport = "";
            reportContent.innerHTML = "<p>No report found.</p>";
        }

        // Display Chart
        // The charts are saved in artifacts/charts/TICKER_chart.png
        // We exposed /artifacts in FastAPI
        const timestamp = new Date().getTime(); // to prevent caching
        chartImage.src = `/artifacts/charts/${ticker}_chart.png?t=${timestamp}`;
        chartImage.classList.remove('hidden');
        
        // Scroll to results smoothly
        resultsPanel.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    const downloadBtn = document.getElementById('download-btn');
    if (downloadBtn) {
        downloadBtn.addEventListener('click', () => {
            if (!currentMarkdownReport) return;
            
            const element = document.getElementById('pdf-content');
            const opt = {
                margin:       0.5,
                filename:     `${currentTicker || 'analysis'}_report.pdf`,
                image:        { type: 'jpeg', quality: 0.98 },
                html2canvas:  { 
                    scale: 2,
                    onclone: (clonedDoc) => {
                        const pdfContent = clonedDoc.getElementById('pdf-content');
                        if (pdfContent) {
                            pdfContent.classList.add('pdf-export-mode');
                            
                            // Add a professional branding header to the top of the PDF
                            const pdfHeader = clonedDoc.createElement('div');
                            pdfHeader.innerHTML = `
                                <div style="text-align: center; margin-bottom: 2rem; padding-bottom: 1rem; border-bottom: 2px solid #000;">
                                    <h1 style="font-size: 24pt; font-weight: bold; margin: 0;">Insight Engine</h1>
                                    <p style="font-size: 12pt; color: #555; margin: 5px 0 0 0;">Autonomous Financial Forecasting & Anomaly Detection</p>
                                </div>
                            `;
                            pdfContent.insertBefore(pdfHeader, pdfContent.firstChild);
                        }
                    }
                },
                jsPDF:        { unit: 'in', format: 'letter', orientation: 'portrait' }
            };
            
            html2pdf().set(opt).from(element).save();
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

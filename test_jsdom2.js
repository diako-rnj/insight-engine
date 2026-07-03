const { JSDOM } = require('jsdom');
const dom = new JSDOM(`
<!DOCTYPE html>
<html>
<body>
    <canvas id="myChart" width="400" height="400"></canvas>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/luxon@3.4.4/build/global/luxon.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-adapter-luxon@1.2.0/dist/chartjs-adapter-luxon.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-chart-financial@0.1.1/dist/chartjs-chart-financial.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/hammerjs@2.0.8/hammer.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-zoom@1.2.1/dist/chartjs-plugin-zoom.js"></script>
    <script>
        window.ResizeObserver = class { observe(){} unobserve(){} disconnect(){} };
        window.onerror = function(msg, url, line, col, error) { 
            console.error("ERROR:", msg);
            if (error) console.error(error.stack);
        };
        const ctx = document.getElementById('myChart').getContext('2d');
        try {
            new Chart(ctx, {
                type: 'candlestick',
                data: {
                    datasets: [{
                        label: 'Historical Data',
                        data: [{x: Date.now(), o: 1, h: 2, l: 0.5, c: 1.5}],
                    }]
                },
                options: {
                    scales: {
                        x: { type: 'time' },
                        y: {  }
                    },
                    plugins: {
                        zoom: {
                            pan: { enabled: true, mode: 'x' },
                            zoom: { mode: 'x' }
                        }
                    }
                }
            });
            console.log("SUCCESS");
        } catch(e) {
            console.error("CAUGHT:", e.stack);
        }
    </script>
</body>
</html>
`, { runScripts: "dangerously", resources: "usable" });

dom.window.document.addEventListener("DOMContentLoaded", () => {
    setTimeout(() => {
        console.log("Done waiting");
    }, 2000);
});

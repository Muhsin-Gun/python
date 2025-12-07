document.addEventListener('DOMContentLoaded', function() {
    const socket = io();
    let currentSymbol = 'EUR/USD';
    let currentTimeframe = '1h';
    let priceChart = null;
    let analysisData = null;

    socket.on('connect', function() {
        document.querySelector('.status-dot').classList.add('connected');
        document.querySelector('.status-text').textContent = 'Connected';
        socket.emit('subscribe', { symbol: currentSymbol });
    });

    socket.on('disconnect', function() {
        document.querySelector('.status-dot').classList.remove('connected');
        document.querySelector('.status-text').textContent = 'Disconnected';
    });

    socket.on('analysis_update', function(data) {
        updateAnalysis(data);
    });

    socket.on('live_narration', function(data) {
        updateNarration(data);
    });

    function updateTime() {
        const now = new Date();
        document.getElementById('timeDisplay').textContent = now.toUTCString().slice(17, 25) + ' UTC';
    }
    setInterval(updateTime, 1000);
    updateTime();

    document.getElementById('symbolSelect').addEventListener('change', function() {
        currentSymbol = this.value;
        document.getElementById('chartSymbol').textContent = currentSymbol;
        socket.emit('subscribe', { symbol: currentSymbol });
        loadMarketData();
    });

    document.querySelectorAll('.tf-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            document.querySelectorAll('.tf-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            currentTimeframe = this.dataset.tf;
            const tfNames = { '1m': '1 Minute', '5m': '5 Minutes', '15m': '15 Minutes', '1h': '1 Hour', '4h': '4 Hours', '1d': '1 Day' };
            document.getElementById('chartTimeframe').textContent = tfNames[currentTimeframe] || currentTimeframe;
            loadMarketData();
        });
    });

    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            this.classList.add('active');
            document.getElementById(this.dataset.tab + '-tab').classList.add('active');
        });
    });

    document.getElementById('analyzeBtn').addEventListener('click', analyzeMarket);
    document.getElementById('backtestBtn').addEventListener('click', runBacktest);
    document.getElementById('runBacktestBtn').addEventListener('click', runBacktest);
    document.getElementById('liveNarrationBtn').addEventListener('click', requestNarration);

    document.getElementById('closeModal').addEventListener('click', function() {
        document.getElementById('signalModal').classList.remove('active');
    });

    function initChart() {
        const ctx = document.getElementById('priceChart').getContext('2d');
        priceChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Price',
                    data: [],
                    borderColor: '#3b82f6',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.1,
                    pointRadius: 0,
                    pointHoverRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    intersect: false,
                    mode: 'index'
                },
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: '#1f2937',
                        titleColor: '#f9fafb',
                        bodyColor: '#9ca3af',
                        borderColor: '#374151',
                        borderWidth: 1,
                        padding: 12,
                        displayColors: false,
                        callbacks: {
                            label: function(context) {
                                return 'Price: ' + context.parsed.y.toFixed(5);
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        display: true,
                        grid: { color: 'rgba(55, 65, 81, 0.3)' },
                        ticks: { color: '#6b7280', maxTicksLimit: 10 }
                    },
                    y: {
                        display: true,
                        position: 'right',
                        grid: { color: 'rgba(55, 65, 81, 0.3)' },
                        ticks: { color: '#6b7280' }
                    }
                }
            }
        });
    }

    function loadMarketData() {
        const encodedSymbol = encodeURIComponent(currentSymbol).replace(/%2F/g, '-');
        fetch(`/api/market-data/${encodedSymbol}?timeframe=${currentTimeframe}&limit=100`)
            .then(response => response.json())
            .then(data => {
                updateChart(data);
                updatePriceDisplay(data);
            })
            .catch(error => console.error('Error loading market data:', error));
    }

    function updateChart(data) {
        if (!priceChart) return;
        
        const labels = data.map(d => {
            const date = new Date(d.timestamp);
            return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
        });
        const prices = data.map(d => d.close);
        
        priceChart.data.labels = labels;
        priceChart.data.datasets[0].data = prices;
        
        const lastPrice = prices[prices.length - 1];
        const firstPrice = prices[0];
        const isPositive = lastPrice >= firstPrice;
        
        priceChart.data.datasets[0].borderColor = isPositive ? '#10b981' : '#ef4444';
        priceChart.data.datasets[0].backgroundColor = isPositive ? 'rgba(16, 185, 129, 0.1)' : 'rgba(239, 68, 68, 0.1)';
        
        priceChart.update('none');
    }

    function updatePriceDisplay(data) {
        if (!data || data.length < 2) return;
        
        const current = data[data.length - 1].close;
        const previous = data[data.length - 2].close;
        const change = current - previous;
        const changePercent = (change / previous * 100).toFixed(4);
        
        document.getElementById('chartPrice').textContent = current.toFixed(5);
        document.getElementById('currentPrice').textContent = current.toFixed(5);
        
        const changeElement = document.getElementById('chartChange');
        const sign = change >= 0 ? '+' : '';
        changeElement.textContent = `${sign}${change.toFixed(5)} (${sign}${changePercent}%)`;
        changeElement.className = 'price-change ' + (change >= 0 ? 'positive' : 'negative');
        
        document.getElementById('priceChange').textContent = `${sign}${changePercent}%`;
        document.getElementById('priceChange').style.color = change >= 0 ? '#10b981' : '#ef4444';
    }

    function analyzeMarket() {
        const btn = document.getElementById('analyzeBtn');
        btn.innerHTML = '<span class="loading"></span> Analyzing...';
        btn.disabled = true;
        
        const encodedSymbol = encodeURIComponent(currentSymbol).replace(/%2F/g, '-');
        fetch(`/api/analysis/${encodedSymbol}?timeframe=${currentTimeframe}`)
            .then(response => response.json())
            .then(data => {
                analysisData = data;
                updateAnalysis({ analysis: data });
                btn.innerHTML = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/></svg> Analyze Market`;
                btn.disabled = false;
            })
            .catch(error => {
                console.error('Error analyzing market:', error);
                btn.innerHTML = 'Analyze Market';
                btn.disabled = false;
            });
    }

    function updateAnalysis(data) {
        const analysis = data.analysis;
        if (!analysis) return;
        
        document.getElementById('trendStatus').textContent = analysis.market_structure?.trend?.toUpperCase() || '--';
        document.getElementById('trendStatus').style.color = 
            analysis.market_structure?.trend === 'bullish' ? '#10b981' :
            analysis.market_structure?.trend === 'bearish' ? '#ef4444' : '#f59e0b';
        
        if (analysis.technical) {
            const rsi = analysis.technical.rsi;
            if (rsi) {
                document.getElementById('rsiValue').textContent = rsi.value?.toFixed(1) || '--';
                document.getElementById('rsiFill').style.width = `${rsi.value || 50}%`;
                document.getElementById('rsiFill').style.background = 
                    rsi.value > 70 ? '#ef4444' : rsi.value < 30 ? '#10b981' : 'linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%)';
            }
            
            const macd = analysis.technical.macd;
            if (macd) {
                document.getElementById('macdValue').textContent = macd.histogram?.toFixed(6) || '--';
                document.getElementById('macdSignal').textContent = macd.signal || 'Neutral';
                document.getElementById('macdSignal').style.color = 
                    macd.signal === 'bullish' ? '#10b981' : macd.signal === 'bearish' ? '#ef4444' : '#9ca3af';
            }
            
            const adx = analysis.technical.adx;
            if (adx) {
                document.getElementById('adxValue').textContent = adx.value?.toFixed(1) || '--';
                document.getElementById('adxSignal').textContent = adx.trend_strength || 'Weak';
            }
            
            const atr = analysis.technical.atr;
            if (atr) {
                document.getElementById('atrValue').textContent = atr.value?.toFixed(6) || '--';
                document.getElementById('atrSignal').textContent = atr.percent > 1.5 ? 'High' : atr.percent > 0.5 ? 'Normal' : 'Low';
            }
        }
        
        updateSignals(analysis.signals);
        updateStructure(analysis.smc, analysis.market_structure);
        updatePatterns(analysis.patterns);
        updatePrediction(analysis.prediction);
        
        if (analysis.signals && analysis.signals.length > 0) {
            document.getElementById('signalGrade').textContent = analysis.signals[0].grade;
            document.getElementById('signalGrade').style.color = getGradeColor(analysis.signals[0].grade);
        }
    }

    function updateSignals(signals) {
        const container = document.getElementById('signalsContainer');
        
        if (!signals || signals.length === 0) {
            container.innerHTML = '<div class="signal-card placeholder"><p>No strong signals detected. Waiting for better setups...</p></div>';
            return;
        }
        
        container.innerHTML = signals.map(signal => `
            <div class="signal-card grade-${signal.grade}">
                <div class="signal-header">
                    <div class="signal-grade ${signal.grade}">${signal.grade}</div>
                    <div class="signal-direction ${signal.direction}">${signal.direction.toUpperCase()}</div>
                </div>
                <div class="signal-details">
                    <div class="signal-detail">
                        <span class="signal-detail-label">Entry</span>
                        <span class="signal-detail-value">${signal.entry_price?.toFixed(5) || '--'}</span>
                    </div>
                    <div class="signal-detail">
                        <span class="signal-detail-label">Stop Loss</span>
                        <span class="signal-detail-value">${signal.stop_loss?.toFixed(5) || '--'}</span>
                    </div>
                    <div class="signal-detail">
                        <span class="signal-detail-label">Take Profit</span>
                        <span class="signal-detail-value">${signal.take_profit?.toFixed(5) || '--'}</span>
                    </div>
                    <div class="signal-detail">
                        <span class="signal-detail-label">R:R</span>
                        <span class="signal-detail-value">${signal.risk_reward?.toFixed(2) || '--'}</span>
                    </div>
                </div>
                <div class="signal-reasoning">${signal.reasoning || 'No reasoning available'}</div>
            </div>
        `).join('');
        
        updateRecentSignals(signals);
    }

    function updateRecentSignals(signals) {
        const container = document.getElementById('recentSignals');
        if (!signals || signals.length === 0) return;
        
        container.innerHTML = signals.slice(0, 5).map(signal => `
            <div class="signal-item" onclick="showSignalDetails('${signal.grade}', '${signal.direction}', ${signal.confidence})">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span class="signal-grade ${signal.grade}" style="width: 28px; height: 28px; font-size: 0.875rem;">${signal.grade}</span>
                    <span class="signal-direction ${signal.direction}" style="font-size: 0.7rem;">${signal.direction.toUpperCase()}</span>
                </div>
                <div style="margin-top: 8px; font-size: 0.75rem; color: #9ca3af;">
                    Confidence: ${(signal.confidence * 100).toFixed(0)}%
                </div>
            </div>
        `).join('');
    }

    function updateStructure(smc, structure) {
        if (structure) {
            document.getElementById('marketStructure').innerHTML = `
                <strong>${structure.structure || 'Unknown'}</strong><br>
                <span style="color: ${structure.trend === 'bullish' ? '#10b981' : structure.trend === 'bearish' ? '#ef4444' : '#f59e0b'}">
                    Trend: ${structure.trend?.toUpperCase() || 'Unknown'}
                </span><br>
                Strength: ${structure.strength?.toFixed(0) || 0}%
                ${structure.bos_detected ? '<br><span style="color: #f59e0b;">Break of Structure Detected</span>' : ''}
                ${structure.choch_detected ? '<br><span style="color: #8b5cf6;">Change of Character Detected</span>' : ''}
            `;
        }
        
        if (smc?.order_blocks) {
            document.getElementById('orderBlocks').innerHTML = smc.order_blocks.slice(-5).map(ob => 
                `<span class="zone-item ${ob.type}">${ob.type.toUpperCase()} @ ${ob.price?.toFixed(5)}</span>`
            ).join('') || '--';
        }
        
        if (smc?.fvgs) {
            document.getElementById('fvgZones').innerHTML = smc.fvgs.slice(-5).map(fvg => 
                `<span class="zone-item ${fvg.type}">${fvg.type.toUpperCase()} FVG</span>`
            ).join('') || '--';
        }
        
        if (smc?.liquidity_zones) {
            document.getElementById('liquidityZones').innerHTML = smc.liquidity_zones.slice(-5).map(zone => 
                `<span class="zone-item">${zone.type}: ${zone.level?.toFixed(5) || '--'}</span>`
            ).join('') || '--';
        }
    }

    function updatePatterns(patterns) {
        const container = document.getElementById('patternsContainer');
        
        if (!patterns || patterns.length === 0) {
            container.innerHTML = '<div class="pattern-card placeholder"><p>No patterns detected</p></div>';
            return;
        }
        
        container.innerHTML = patterns.slice(-6).map(pattern => `
            <div class="pattern-card ${pattern.direction}">
                <div class="pattern-type">${formatPatternType(pattern.type)}</div>
                <div class="pattern-description">${pattern.description || ''}</div>
                <div style="margin-top: 8px; font-size: 0.7rem; color: #6b7280;">
                    Strength: ${pattern.strength || 'moderate'}
                </div>
            </div>
        `).join('');
    }

    function updatePrediction(prediction) {
        if (!prediction || !prediction.scenarios) return;
        
        const scenarios = prediction.scenarios;
        
        if (scenarios.bullish) {
            document.getElementById('bullishProb').textContent = `${scenarios.bullish.probability}%`;
            document.getElementById('bullishTarget').textContent = `Target: ${scenarios.bullish.target?.toFixed(5) || '--'}`;
        }
        
        if (scenarios.neutral) {
            document.getElementById('neutralProb').textContent = `${scenarios.neutral.probability}%`;
            document.getElementById('neutralTarget').textContent = `Range bound`;
        }
        
        if (scenarios.bearish) {
            document.getElementById('bearishProb').textContent = `${scenarios.bearish.probability}%`;
            document.getElementById('bearishTarget').textContent = `Target: ${scenarios.bearish.target?.toFixed(5) || '--'}`;
        }
    }

    function runBacktest() {
        const btn = document.getElementById('runBacktestBtn');
        const strategy = document.getElementById('strategySelect').value;
        const capital = parseFloat(document.getElementById('capitalInput').value) || 10000;
        
        btn.innerHTML = '<span class="loading"></span> Running Backtest...';
        btn.disabled = true;
        
        document.getElementById('backtestResults').innerHTML = '<div class="backtest-placeholder"><span class="loading"></span> Running 5x backtest iterations...</div>';
        
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
        document.querySelector('[data-tab="backtest"]').classList.add('active');
        document.getElementById('backtest-tab').classList.add('active');
        
        fetch('/api/backtest', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ symbol: currentSymbol, strategy: strategy, initial_capital: capital })
        })
        .then(response => response.json())
        .then(data => {
            displayBacktestResults(data);
            btn.innerHTML = 'Run 5x Backtest';
            btn.disabled = false;
        })
        .catch(error => {
            console.error('Error running backtest:', error);
            document.getElementById('backtestResults').innerHTML = '<div class="backtest-placeholder">Error running backtest. Please try again.</div>';
            btn.innerHTML = 'Run 5x Backtest';
            btn.disabled = false;
        });
    }

    function displayBacktestResults(data) {
        const container = document.getElementById('backtestResults');
        
        const returnClass = data.total_return >= 0 ? 'positive' : 'negative';
        const returnSign = data.total_return >= 0 ? '+' : '';
        
        container.innerHTML = `
            <div class="backtest-metrics">
                <div class="metric-card">
                    <div class="metric-value ${returnClass}">${returnSign}${data.total_return?.toFixed(2)}%</div>
                    <div class="metric-label">Total Return</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">${data.win_rate?.toFixed(1)}%</div>
                    <div class="metric-label">Win Rate</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">${data.sharpe_ratio?.toFixed(2)}</div>
                    <div class="metric-label">Sharpe Ratio</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value negative">-${data.max_drawdown?.toFixed(2)}%</div>
                    <div class="metric-label">Max Drawdown</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">${data.total_trades}</div>
                    <div class="metric-label">Total Trades</div>
                </div>
            </div>
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 20px;">
                <div class="metric-card">
                    <div class="metric-value positive">${data.total_pips?.toFixed(1)}</div>
                    <div class="metric-label">Total Pips</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">${data.profit_factor?.toFixed(2)}</div>
                    <div class="metric-label">Profit Factor</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">$${data.final_capital?.toFixed(2)}</div>
                    <div class="metric-label">Final Capital</div>
                </div>
            </div>
            <div style="background: #1f2937; padding: 16px; border-radius: 8px;">
                <h4 style="margin-bottom: 12px; font-size: 0.875rem;">Performance by Signal Grade</h4>
                <div style="display: flex; gap: 12px; flex-wrap: wrap;">
                    ${Object.entries(data.grade_distribution || {}).map(([grade, stats]) => `
                        <div style="background: #374151; padding: 12px; border-radius: 6px; min-width: 100px;">
                            <span class="signal-grade ${grade}" style="width: 24px; height: 24px; font-size: 0.75rem; display: inline-flex;">${grade}</span>
                            <div style="margin-top: 8px; font-size: 0.75rem;">
                                <div>Trades: ${stats.count}</div>
                                <div>Win Rate: ${stats.win_rate?.toFixed(1)}%</div>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    function requestNarration() {
        const btn = document.getElementById('liveNarrationBtn');
        btn.innerHTML = '<span class="loading"></span> Loading...';
        
        socket.emit('request_live_narration', { 
            symbol: currentSymbol, 
            timeframe: currentTimeframe 
        });
        
        setTimeout(() => {
            btn.innerHTML = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/>
                <path d="M19 10v2a7 7 0 0 1-14 0v-2M12 19v4M8 23h8"/>
            </svg> Live Narration`;
        }, 1000);
    }

    function updateNarration(data) {
        const box = document.getElementById('narrationBox');
        box.innerHTML = data.narration?.narration || data.narration || 'No narration available';
    }

    function getGradeColor(grade) {
        const colors = {
            'S': '#8b5cf6',
            'A': '#10b981',
            'B': '#3b82f6',
            'C': '#f59e0b',
            'D': '#6b7280',
            'E': '#ef4444'
        };
        return colors[grade] || '#6b7280';
    }

    function formatPatternType(type) {
        return type.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
    }

    window.showSignalDetails = function(grade, direction, confidence) {
        const modal = document.getElementById('signalModal');
        const body = document.getElementById('modalBody');
        body.innerHTML = `
            <div style="text-align: center; padding: 20px;">
                <div class="signal-grade ${grade}" style="width: 60px; height: 60px; font-size: 1.5rem; margin: 0 auto 16px;">${grade}</div>
                <h3 style="margin-bottom: 8px;">${direction.toUpperCase()} Signal</h3>
                <p style="color: #9ca3af;">Confidence: ${(confidence * 100).toFixed(0)}%</p>
            </div>
        `;
        modal.classList.add('active');
    };

    initChart();
    loadMarketData();
    
    setInterval(loadMarketData, 60000);
});

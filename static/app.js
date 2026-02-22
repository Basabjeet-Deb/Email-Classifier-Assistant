let currentEmails = [];
let accountsList = [];
let activeAccount = "default";

// Dismiss dropdown when clicking outside
window.addEventListener('click', function (e) {
    const avatar = document.getElementById('activeAvatar');
    const dropdown = document.getElementById('accountDropdown');
    if (avatar && dropdown && !avatar.contains(e.target) && !dropdown.contains(e.target)) {
        dropdown.classList.remove('show');
    }
});

window.onload = async () => {
    await fetchStatus();
};

function toggleDropdown() {
    document.getElementById('accountDropdown').classList.toggle('show');
}

async function fetchStatus() {
    try {
        const res = await fetch('/api/status');
        const data = await res.json();
        const statusText = document.getElementById('statusText');

        if (data.status === 'connected') {
            statusText.textContent = 'Connected';
            accountsList = data.accounts || [];

            if (accountsList.length > 0) {
                if (!accountsList.includes(activeAccount)) {
                    activeAccount = accountsList[0];
                }
            }
            renderAccountSwitcher();
        } else {
            statusText.textContent = 'Auth Required';
            accountsList = [];
            renderAccountSwitcher();
        }
    } catch (e) {
        console.error('Could not reach API:', e);
        document.getElementById('statusText').textContent = 'Disconnected';
    }
}

function renderAccountSwitcher() {
    const dropdown = document.getElementById('accountDropdown');
    const avatar = document.getElementById('activeAvatar');

    // Render Avatar letter
    const displayLetter = activeAccount === 'default' ? 'D' : activeAccount.charAt(0).toUpperCase();
    avatar.innerText = displayLetter;

    // Render dropdown
    let html = `
        <div class="dropdown-active-account">
            <div class="avatar-large">${displayLetter}</div>
            <div class="dropdown-active-email">${activeAccount === 'default' ? 'Default Profile' : activeAccount}</div>
            <div class="dropdown-active-label">Active Workspace</div>
        </div>
        <div class="dropdown-list">
    `;

    // Render other accounts
    accountsList.forEach(acc => {
        if (acc !== activeAccount) {
            const l = acc === 'default' ? 'D' : acc.charAt(0).toUpperCase();
            html += `
                <div class="dropdown-item" onclick="switchAccount('${acc}')">
                    <div class="avatar-small">${l}</div>
                    <div style="font-size: 0.9rem; color: var(--text-primary);">${acc === 'default' ? 'Default Profile' : acc}</div>
                </div>
            `;
        }
    });

    html += `</div>`;
    html += `<button class="dropdown-add-btn" onclick="addNewAccount()">+ Add another account</button>`;

    dropdown.innerHTML = html;
}

function switchAccount(acc) {
    activeAccount = acc;
    document.getElementById('accountDropdown').classList.remove('show');
    currentEmails = [];
    renderEmails();
    renderAccountSwitcher();
}

async function addNewAccount() {
    try {
        await fetch('/api/auth', { method: 'POST' });
        await fetchStatus();
    } catch (e) {
        alert('Failed to add account');
    }
}


async function scanInbox() {
    const maxResults = parseInt(document.getElementById('scanLimit').value);
    const query = document.getElementById('scanType').value;
    const btn = document.getElementById('btnScan');
    const icon = document.getElementById('scanIcon');
    const text = document.getElementById('scanText');

    btn.disabled = true;
    icon.innerHTML = '<div class="spinner"></div>';
    text.textContent = 'Analyzing...';

    try {
        const res = await fetch('/api/scan', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                account_id: activeAccount,
                max_results: maxResults,
                query: query
            })
        });
        const data = await res.json();

        if (data.status === 'success') {
            currentEmails = data.emails;
            document.getElementById('totalScanned').textContent = currentEmails.length;

            if (data.metrics && data.metrics.avg_confidence) {
                const conf = (data.metrics.avg_confidence * 100).toFixed(0);
                document.getElementById('avgConfidence').textContent = conf + '%';
            }

            document.getElementById('tableStats').textContent =
                `${currentEmails.length} emails analyzed in ${(data.processing_time_ms / 1000).toFixed(1)}s`;

            renderEmails();
        } else {
            alert('Error: ' + (data.detail || 'Unknown error'));
        }
    } catch (e) {
        alert('Server error: ' + e.message);
    }

    btn.disabled = false;
    icon.textContent = '🚀';
    text.textContent = 'Analyze Inbox';
}

function getBadgeClass(category) {
    if (category.includes('Banking')) return 'badge-banking';
    if (category.includes('Receipts')) return 'badge-receipts';
    if (category.includes('Work')) return 'badge-work';
    if (category.includes('Social')) return 'badge-social';
    if (category.includes('Newsletter')) return 'badge-newsletters';
    if (category.includes('Personal')) return 'badge-personal';
    if (category.includes('Spam')) return 'badge-spam';
    return 'badge-other';
}

function isProtected(category) {
    return category.includes('Banking') || category.includes('Personal') ||
        category.includes('Work') || category.includes('Receipts');
}

function renderEmails() {
    const tbody = document.getElementById('emailList');
    document.getElementById('selectAll').checked = false;
    updateDeleteButton();

    if (currentEmails.length === 0) {
        tbody.innerHTML = `
            <tr><td colspan="5">
                <div class="empty-state">
                    <div class="empty-icon">📭</div>
                    <p>No emails found</p>
                </div>
            </td></tr>`;
        return;
    }

    let html = '';
    currentEmails.forEach(email => {
        const protected = isProtected(email.category);
        const badgeClass = getBadgeClass(email.category);
        const confidence = Math.round((email.confidence || 0) * 100);

        const checkboxHtml = protected
            ? `<span title="Protected">🔒</span>`
            : `<input type="checkbox" class="email-cb" value="${email.id}" onchange="updateDeleteButton()">`;

        html += `
            <tr>
                <td>${checkboxHtml}</td>
                <td><span class="badge ${badgeClass}">${email.category}</span></td>
                <td>
                    <div class="confidence-bar">
                        <div class="confidence-fill" style="width: ${confidence}%"></div>
                    </div>
                    <div style="font-size: 0.7rem; color: var(--text-muted); margin-top: 0.25rem;">${confidence}%</div>
                </td>
                <td style="color: var(--text-secondary);">${email.sender.split('<')[0].substring(0, 30)}</td>
                <td>
                    <div style="font-weight: 500; margin-bottom: 0.25rem;">${email.subject || '(No Subject)'}</div>
                    <div style="color: var(--text-muted); font-size: 0.8rem;">${email.snippet.substring(0, 100)}...</div>
                </td>
            </tr>
        `;
    });
    tbody.innerHTML = html;
}

function toggleSelectAll() {
    const master = document.getElementById('selectAll');
    const checkboxes = document.querySelectorAll('.email-cb');
    checkboxes.forEach(cb => cb.checked = master.checked);
    updateDeleteButton();
}

function updateDeleteButton() {
    const checked = document.querySelectorAll('.email-cb:checked');
    const btn = document.getElementById('btnDelete');
    const text = document.getElementById('deleteText');

    if (checked.length > 0) {
        btn.disabled = false;
        text.textContent = `Delete (${checked.length})`;
    } else {
        btn.disabled = true;
        text.textContent = 'Delete (0)';
    }
}

async function deleteSelected() {
    const checked = document.querySelectorAll('.email-cb:checked');
    if (checked.length === 0) return;

    if (!confirm(`Move ${checked.length} email(s) to trash?`)) return;

    const idsToDelete = Array.from(checked).map(cb => cb.value);
    const btn = document.getElementById('btnDelete');
    const icon = document.getElementById('deleteIcon');

    btn.disabled = true;
    icon.innerHTML = '<div class="spinner"></div>';

    try {
        const res = await fetch('/api/delete', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                account_id: activeAccount,
                message_ids: idsToDelete
            })
        });
        const data = await res.json();

        if (data.status === 'success') {
            currentEmails = currentEmails.filter(e => !idsToDelete.includes(e.id));
            renderEmails();
            document.getElementById('totalScanned').textContent = currentEmails.length;
        } else {
            alert('Error: ' + (data.detail || 'Unknown error'));
        }
    } catch (e) {
        alert('Server error: ' + e.message);
    }

    icon.textContent = '🗑️';
    updateDeleteButton();
}


// ============================================
// ANALYTICS FUNCTIONALITY
// ============================================

let analyticsCharts = {};

function switchView(view) {
    // Update tabs
    document.getElementById('inboxTab').classList.remove('active');
    document.getElementById('analyticsTab').classList.remove('active');
    
    // Update views
    document.getElementById('inboxView').classList.remove('active');
    document.getElementById('analyticsView').classList.remove('active');
    
    if (view === 'inbox') {
        document.getElementById('inboxTab').classList.add('active');
        document.getElementById('inboxView').classList.add('active');
    } else {
        document.getElementById('analyticsTab').classList.add('active');
        document.getElementById('analyticsView').classList.add('active');
        loadAnalytics();
    }
}

async function loadAnalytics() {
    const days = parseInt(document.getElementById('analyticsTimeRange').value);
    
    try {
        const res = await fetch(`/api/analytics/${activeAccount}?days=${days}`);
        const data = await res.json();
        
        if (data.status === 'success') {
            renderAnalytics(data.analytics, data.insights);
        } else {
            console.error('Analytics error:', data);
        }
    } catch (e) {
        console.error('Failed to load analytics:', e);
    }
}

function renderAnalytics(analytics, insights) {
    // Update key metrics
    document.getElementById('metricTotalEmails').textContent = analytics.total_emails.toLocaleString();
    document.getElementById('metricAvgConfidence').textContent = analytics.average_confidence + '%';
    document.getElementById('metricAvgTime').textContent = analytics.average_processing_time + 'ms';
    
    // Determine overall sentiment
    const sentDist = analytics.sentiment_distribution;
    const totalSent = Object.values(sentDist).reduce((a, b) => a + b, 0);
    if (totalSent > 0) {
        const posRatio = (sentDist.POSITIVE || 0) / totalSent;
        const negRatio = (sentDist.NEGATIVE || 0) / totalSent;
        let mood = 'Neutral';
        if (posRatio > 0.5) mood = 'Positive';
        else if (negRatio > 0.4) mood = 'Negative';
        document.getElementById('metricSentiment').textContent = mood;
    }
    
    // Render insights
    renderInsights(insights);
    
    // Render charts
    renderCategoryChart(analytics.category_distribution);
    renderTrendChart(analytics.daily_trend);
    renderHourlyChart(analytics.emails_by_hour);
    renderWeeklyChart(analytics.emails_by_day);
    renderSendersChart(analytics.top_senders);
    renderSentimentChart(analytics.sentiment_distribution);
}

function renderInsights(insights) {
    const container = document.getElementById('insightsList');
    
    if (insights.length === 0) {
        container.innerHTML = `
            <div class="insight-item">
                <span class="insight-icon">📊</span>
                <span>No insights available yet. Scan some emails to generate insights!</span>
            </div>
        `;
        return;
    }
    
    let html = '';
    insights.forEach(insight => {
        html += `
            <div class="insight-item">
                <span class="insight-icon">💡</span>
                <span>${insight}</span>
            </div>
        `;
    });
    container.innerHTML = html;
}

function renderCategoryChart(categories) {
    const ctx = document.getElementById('categoryChart');
    
    if (analyticsCharts.category) {
        analyticsCharts.category.destroy();
    }
    
    const labels = categories.map(c => c.category);
    const data = categories.map(c => c.count);
    const colors = labels.map(label => getCategoryColor(label));
    
    analyticsCharts.category = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: colors,
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 15,
                        font: { size: 12 }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((context.parsed / total) * 100).toFixed(1);
                            return `${context.label}: ${context.parsed} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

function renderTrendChart(dailyData) {
    const ctx = document.getElementById('trendChart');
    
    if (analyticsCharts.trend) {
        analyticsCharts.trend.destroy();
    }
    
    const labels = dailyData.map(d => {
        const date = new Date(d.date);
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    });
    const data = dailyData.map(d => d.count);
    
    analyticsCharts.trend = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Emails per Day',
                data: data,
                borderColor: '#3b82f6',
                backgroundColor: 'rgba(59, 130, 246, 0.1)',
                fill: true,
                tension: 0.4,
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: { precision: 0 }
                }
            }
        }
    });
}

function renderHourlyChart(hourlyData) {
    const ctx = document.getElementById('hourlyChart');
    
    if (analyticsCharts.hourly) {
        analyticsCharts.hourly.destroy();
    }
    
    const labels = hourlyData.map((_, i) => {
        const hour = i % 12 || 12;
        const period = i < 12 ? 'AM' : 'PM';
        return `${hour}${period}`;
    });
    
    analyticsCharts.hourly = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Emails',
                data: hourlyData,
                backgroundColor: 'rgba(6, 182, 212, 0.6)',
                borderColor: '#06b6d4',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: { precision: 0 }
                }
            }
        }
    });
}

function renderWeeklyChart(weeklyData) {
    const ctx = document.getElementById('weeklyChart');
    
    if (analyticsCharts.weekly) {
        analyticsCharts.weekly.destroy();
    }
    
    const labels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
    
    analyticsCharts.weekly = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Emails',
                data: weeklyData,
                backgroundColor: 'rgba(139, 92, 246, 0.6)',
                borderColor: '#8b5cf6',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: { precision: 0 }
                }
            }
        }
    });
}

function renderSendersChart(topSenders) {
    const ctx = document.getElementById('sendersChart');
    
    if (analyticsCharts.senders) {
        analyticsCharts.senders.destroy();
    }
    
    const labels = topSenders.map(s => s.sender.length > 20 ? s.sender.substring(0, 20) + '...' : s.sender);
    const data = topSenders.map(s => s.count);
    
    analyticsCharts.senders = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Emails',
                data: data,
                backgroundColor: 'rgba(16, 185, 129, 0.6)',
                borderColor: '#10b981',
                borderWidth: 1
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    ticks: { precision: 0 }
                }
            }
        }
    });
}

function renderSentimentChart(sentimentData) {
    const ctx = document.getElementById('sentimentChart');
    
    if (analyticsCharts.sentiment) {
        analyticsCharts.sentiment.destroy();
    }
    
    const labels = Object.keys(sentimentData);
    const data = Object.values(sentimentData);
    const colors = {
        'POSITIVE': 'rgba(16, 185, 129, 0.8)',
        'NEGATIVE': 'rgba(239, 68, 68, 0.8)',
        'NEUTRAL': 'rgba(100, 116, 139, 0.8)'
    };
    const bgColors = labels.map(l => colors[l] || 'rgba(100, 116, 139, 0.8)');
    
    analyticsCharts.sentiment = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: bgColors,
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 15,
                        font: { size: 12 }
                    }
                }
            }
        }
    });
}

function getCategoryColor(category) {
    if (category.includes('Banking')) return 'rgba(16, 185, 129, 0.8)';
    if (category.includes('Receipts')) return 'rgba(59, 130, 246, 0.8)';
    if (category.includes('Work')) return 'rgba(139, 92, 246, 0.8)';
    if (category.includes('Social')) return 'rgba(236, 72, 153, 0.8)';
    if (category.includes('Newsletter')) return 'rgba(245, 158, 11, 0.8)';
    if (category.includes('Personal')) return 'rgba(99, 102, 241, 0.8)';
    if (category.includes('Spam')) return 'rgba(239, 68, 68, 0.8)';
    return 'rgba(100, 116, 139, 0.8)';
}

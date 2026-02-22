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

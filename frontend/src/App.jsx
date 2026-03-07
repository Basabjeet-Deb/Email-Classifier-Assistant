import { useState, useEffect } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'react-hot-toast';
import toast from 'react-hot-toast';
import { LandingPage } from './components/LandingPage';
import { Layout } from './components/Layout';
import { StatsCards } from './components/StatsCards';
import { EmailTableEnhanced } from './components/EmailTableEnhanced';
import { AIInsightsDashboard } from './components/AIInsightsDashboard';
import { Analytics } from './components/Analytics';
import { Settings } from './components/Settings';
import { useEmails } from './hooks/useEmails';
import { emailAPI } from './api/client';
import { Rocket, Trash2, RefreshCw } from 'lucide-react';

const queryClient = new QueryClient();

function AppContent() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isCheckingAuth, setIsCheckingAuth] = useState(true);
  const [activeView, setActiveView] = useState('inbox');
  const [status, setStatus] = useState('Checking...');
  const [activeAccount, setActiveAccount] = useState('default');
  const [availableAccounts, setAvailableAccounts] = useState([]);
  const [selectedIds, setSelectedIds] = useState([]);
  const [scanLimit, setScanLimit] = useState(50);
  const [searchQuery, setSearchQuery] = useState('');

  const { emails, loading, metrics, scanInbox, deleteEmails } = useEmails();

  useEffect(() => {
    checkStatus();
    
    // Check for OAuth callback parameters
    const urlParams = new URLSearchParams(window.location.search);
    const authStatus = urlParams.get('auth');
    const email = urlParams.get('email');
    const message = urlParams.get('message');
    
    if (authStatus === 'success') {
      toast.success(`Successfully authenticated: ${email}`);
      // Clean up URL
      window.history.replaceState({}, document.title, window.location.pathname);
      checkStatus();
    } else if (authStatus === 'error') {
      toast.error(`Authentication failed: ${message || 'Unknown error'}`);
      window.history.replaceState({}, document.title, window.location.pathname);
    }
  }, []);

  const checkStatus = async () => {
    try {
      const response = await emailAPI.getStatus();
      if (response.data.status === 'connected') {
        setStatus('Connected');
        setIsAuthenticated(true);
        if (response.data.accounts && response.data.accounts.length > 0) {
          setAvailableAccounts(response.data.accounts);
          setActiveAccount(response.data.accounts[0]);
        }
      } else {
        setStatus('Disconnected');
        setIsAuthenticated(false);
        setAvailableAccounts([]);
      }
    } catch (error) {
      setStatus('Error');
      setIsAuthenticated(false);
      setAvailableAccounts([]);
    } finally {
      setIsCheckingAuth(false);
    }
  };

  const handleLogin = async () => {
    try {
      const response = await emailAPI.startAuth();
      const { authorization_url } = response.data;
      
      // Redirect user to Google OAuth page
      window.location.href = authorization_url;
    } catch (error) {
      console.error('Auth error:', error);
      toast.error('Failed to start authentication');
    }
  };

  const handleAddAccount = async () => {
    try {
      const response = await emailAPI.startAuth();
      const { authorization_url } = response.data;
      
      // Open in new window for adding additional accounts
      window.open(authorization_url, '_blank', 'width=600,height=700');
      
      toast.success('Authentication window opened. Complete the process there.');
      
      // Poll for status updates
      const pollInterval = setInterval(async () => {
        const statusResponse = await emailAPI.getStatus();
        if (statusResponse.data.accounts.length > availableAccounts.length) {
          clearInterval(pollInterval);
          await checkStatus();
          toast.success('New account added successfully!');
        }
      }, 2000);
      
      // Stop polling after 2 minutes
      setTimeout(() => clearInterval(pollInterval), 120000);
    } catch (error) {
      console.error('Auth error:', error);
      toast.error('Failed to add account');
    }
  };

  const handleAccountSwitch = (account) => {
    setActiveAccount(account);
    setSelectedIds([]);
    toast.success(`Switched to ${account}`);
  };

  const handleScan = async () => {
    setSelectedIds([]);

    const toastId = toast.loading(
      <div className="flex flex-col gap-1">
        <span className="font-semibold">Scanning Inbox...</span>
        <span className="text-sm text-neutral-400">Fetching and classifying emails</span>
      </div>
    );

    try {
      await scanInbox(activeAccount, scanLimit, 'in:inbox category:promotions OR is:unread');

      toast.success(
        <div className="flex flex-col gap-1">
          <span className="font-semibold">Scan Complete!</span>
          <span className="text-sm text-neutral-400">Emails classified successfully</span>
        </div>,
        { id: toastId, duration: 3000 }
      );
    } catch (error) {
      toast.error(
        error.response?.status === 429
          ? 'Rate limit reached. Please wait and try again.'
          : 'Scan failed. Please try again.',
        { id: toastId, duration: 4000 }
      );
    }
  };

  const handleDelete = async () => {
    if (selectedIds.length === 0) return;
    if (!confirm(`Delete ${selectedIds.length} email(s)?`)) return;

    const count = selectedIds.length;
    const idsToDelete = [...selectedIds];

    const toastId = toast.loading(
      <div className="flex flex-col gap-1">
        <span className="font-semibold">Deleting {count} email{count !== 1 ? 's' : ''}...</span>
        <span className="text-sm text-neutral-400">Removing from inbox</span>
      </div>
    );

    setSelectedIds([]);

    try {
      await deleteEmails(activeAccount, idsToDelete, toastId);

      toast.success(
        <div className="flex flex-col gap-1">
          <span className="font-semibold">Deleted Successfully!</span>
          <span className="text-sm text-neutral-400">{count} email{count !== 1 ? 's' : ''} removed</span>
        </div>,
        { id: toastId, duration: 3000 }
      );
    } catch (error) {
      setSelectedIds(idsToDelete);

      toast.error(
        <div className="flex flex-col gap-1">
          <span className="font-semibold">Delete Failed</span>
          <span className="text-sm text-neutral-400">Please try again</span>
        </div>,
        { id: toastId, duration: 4000 }
      );
    }
  };

  const handleArchive = async (emailId) => {
    try {
      await emailAPI.archiveEmails({
        account_id: activeAccount,
        message_ids: [emailId]
      });
      toast.success('Email archived successfully!');
      setSelectedIds(prev => prev.filter(id => id !== emailId));
    } catch (error) {
      console.error('Failed to archive email:', error);
      toast.error('Failed to archive email');
    }
  };

  const handleToggleSelect = (id) => {
    setSelectedIds(prev =>
      prev.includes(id) ? prev.filter(i => i !== id) : [...prev, id]
    );
  };

  const handleToggleSelectAll = () => {
    const selectableEmails = emails.filter(e =>
      !['Banking/Financial', 'Work/Career', 'Shopping/Orders'].some(c => e.category.includes(c))
    );

    if (selectedIds.length === selectableEmails.length) {
      setSelectedIds([]);
    } else {
      setSelectedIds(selectableEmails.map(e => e.id));
    }
  };

  const totalScanned = emails.length;
  const avgConfidence = metrics?.avg_confidence
    ? Math.round(metrics.avg_confidence * 100)
    : 0;

  const filteredEmails = searchQuery
    ? emails.filter(email =>
      email.subject?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      email.sender?.toLowerCase().includes(searchQuery.toLowerCase())
    )
    : emails;

  // Show landing page if not authenticated
  if (isCheckingAuth) {
    return (
      <div className="flex items-center justify-center h-screen bg-neutral-900">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-primary-200 border-t-primary-600 rounded-full animate-spin mx-auto mb-4" />
          <p className="text-neutral-400">Loading...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <LandingPage onLogin={handleLogin} />;
  }

  return (
    <Layout
      activeView={activeView}
      setActiveView={setActiveView}
      status={status}
      activeAccount={activeAccount}
      searchQuery={searchQuery}
      setSearchQuery={setSearchQuery}
      availableAccounts={availableAccounts}
      onAccountSwitch={handleAccountSwitch}
      onAddAccount={handleAddAccount}
    >
      {activeView === 'inbox' ? (
        <div className="space-y-5">
          {/* Rate Limit Info Banner */}
          <div className="glass rounded-lg p-3.5 flex items-start gap-3 border-l-2 border-amber-500/40">
            <div className="flex-shrink-0 mt-0.5">
              <svg className="w-4 h-4 text-amber-400" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="flex-1">
              <h4 className="text-[12px] font-semibold text-amber-300 mb-0.5">Gmail API Rate Limits</h4>
              <p className="text-[11px] text-neutral-400">
                Start with 10 emails to avoid rate limits. Wait 30-60 seconds between scans if you hit limits.
              </p>
            </div>
          </div>

          {/* Page Header */}
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-xl font-bold text-neutral-100">Inbox Classification</h1>
              <p className="text-neutral-500 mt-0.5 text-sm">
                {searchQuery
                  ? `Found ${filteredEmails.length} result${filteredEmails.length !== 1 ? 's' : ''} for "${searchQuery}"`
                  : 'AI-powered email organization'
                }
              </p>
            </div>

            <div className="flex items-center gap-2.5">
              <select
                value={scanLimit}
                onChange={(e) => setScanLimit(Number(e.target.value))}
                className="px-3 py-2 bg-dark-800 border border-white/[0.06] rounded-lg text-[12px] text-neutral-300 focus:outline-none focus:ring-1 focus:ring-primary-500/30"
              >
                <option value={10}>10 emails (Recommended)</option>
                <option value={25}>25 emails</option>
                <option value={50}>50 emails</option>
              </select>

              <button
                onClick={handleScan}
                disabled={loading}
                className="flex items-center gap-2 px-5 py-2 bg-primary-600/80 text-white rounded-lg hover:bg-primary-600 transition-all disabled:opacity-50 disabled:cursor-not-allowed text-[13px] font-medium"
              >
                {loading ? (
                  <>
                    <RefreshCw size={16} className="animate-spin" />
                    <span>Analyzing...</span>
                  </>
                ) : (
                  <>
                    <Rocket size={16} />
                    <span>Analyze Inbox</span>
                  </>
                )}
              </button>

              {selectedIds.length > 0 && (
                <button
                  onClick={handleDelete}
                  className="flex items-center gap-2 px-4 py-2 bg-red-500/10 text-red-400 rounded-lg hover:bg-red-500/15 transition-all text-[13px] font-medium"
                >
                  <Trash2 size={16} />
                  <span>Delete ({selectedIds.length})</span>
                </button>
              )}
            </div>
          </div>

          {/* Stats Cards */}
          <StatsCards
            totalScanned={totalScanned}
            avgConfidence={avgConfidence}
            metrics={metrics}
          />

          {/* Email Table */}
          <EmailTableEnhanced
            emails={filteredEmails}
            selectedIds={selectedIds}
            onToggleSelect={handleToggleSelect}
            onToggleSelectAll={handleToggleSelectAll}
            onDelete={handleDelete}
            onArchive={handleArchive}
            searchQuery={searchQuery}
          />

          {/* AI Insights Dashboard */}
          {emails.length > 0 && (
            <div className="mt-6">
              <AIInsightsDashboard emails={emails} metrics={metrics} />
            </div>
          )}
        </div>
      ) : activeView === 'analytics' ? (
        <Analytics activeAccount={activeAccount} />
      ) : activeView === 'settings' ? (
        <Settings />
      ) : null}
    </Layout>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AppContent />
      <Toaster
        position="top-right"
        containerStyle={{
          top: 80,
          right: 20,
          zIndex: 9999,
        }}
        toastOptions={{
          style: {
            background: '#1f1f27',
            color: '#e0ddd6',
            border: '1px solid rgba(255, 255, 255, 0.06)',
            boxShadow: '0 4px 20px rgba(0, 0, 0, 0.4)',
            fontSize: '13px',
            zIndex: 9999,
          },
        }}
      />
    </QueryClientProvider>
  );
}

export default App;

import { useState, useEffect } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'react-hot-toast';
import toast from 'react-hot-toast';
import { Layout } from './components/Layout';
import { StatsCards } from './components/StatsCards';
import { EmailTableModern } from './components/EmailTableModern';
import { Analytics } from './components/Analytics';
import { Settings } from './components/Settings';
import { useEmails } from './hooks/useEmails';
import { emailAPI } from './api/client';
import { Rocket, Trash2, RefreshCw } from 'lucide-react';

const queryClient = new QueryClient();

function AppContent() {
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
  }, []);

  const checkStatus = async () => {
    try {
      const response = await emailAPI.getStatus();
      if (response.data.status === 'connected') {
        setStatus('Connected');
        if (response.data.accounts && response.data.accounts.length > 0) {
          setAvailableAccounts(response.data.accounts);
          setActiveAccount(response.data.accounts[0]);
        }
      } else {
        setStatus('Disconnected');
        setAvailableAccounts([]);
      }
    } catch (error) {
      setStatus('Error');
      setAvailableAccounts([]);
    }
  };

  const handleAccountSwitch = (account) => {
    setActiveAccount(account);
    setSelectedIds([]);
    toast.success(`Switched to ${account}`);
  };

  const handleAddAccount = async () => {
    try {
      await emailAPI.authenticate();
      toast.success('Account authentication started. Check your browser.');
      // Refresh status after authentication
      setTimeout(() => checkStatus(), 2000);
    } catch (error) {
      toast.error('Failed to add account');
    }
  };

  const handleScan = async () => {
    setSelectedIds([]);
    try {
      await scanInbox(activeAccount, scanLimit, 'in:inbox category:promotions OR is:unread');
    } catch (error) {
      if (error.response?.status === 429) {
        toast.error('Rate limit reached. Please wait a moment and try again.', {
          duration: 5000
        });
      }
    }
  };

  const handleDelete = async () => {
    if (selectedIds.length === 0) return;
    if (!confirm(`Delete ${selectedIds.length} email(s)?`)) return;
    await deleteEmails(activeAccount, selectedIds);
    setSelectedIds([]);
  };

  const handleArchive = async (emailId) => {
    try {
      await emailAPI.archiveEmails({
        account_id: activeAccount,
        message_ids: [emailId]
      });
      toast.success('Email archived successfully!');
      // Remove from local state
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

  // Filter emails based on search query
  const filteredEmails = searchQuery
    ? emails.filter(email =>
        email.subject?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        email.sender?.toLowerCase().includes(searchQuery.toLowerCase())
      )
    : emails;

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
        <div className="space-y-6">
          {/* Rate Limit Info Banner */}
          <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 flex items-start gap-3">
            <div className="flex-shrink-0 mt-0.5">
              <svg className="w-5 h-5 text-amber-600" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="flex-1">
              <h4 className="text-sm font-semibold text-amber-900 mb-1">Gmail API Rate Limits</h4>
              <p className="text-sm text-amber-700">
                Start with 10 emails to avoid rate limits. Wait 30-60 seconds between scans if you hit limits.
              </p>
            </div>
          </div>

          {/* Page Header */}
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-neutral-900">Inbox Classification</h1>
              <p className="text-neutral-500 mt-1">
                {searchQuery 
                  ? `Found ${filteredEmails.length} result${filteredEmails.length !== 1 ? 's' : ''} for "${searchQuery}"`
                  : 'AI-powered email organization'
                }
              </p>
            </div>
            
            <div className="flex items-center gap-3">
              <select
                value={scanLimit}
                onChange={(e) => setScanLimit(Number(e.target.value))}
                className="px-4 py-2 bg-white border border-neutral-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option value={10}>10 emails (Recommended)</option>
                <option value={25}>25 emails</option>
                <option value={50}>50 emails</option>
              </select>

              <button
                onClick={handleScan}
                disabled={loading}
                className="flex items-center gap-2 px-6 py-2 bg-gradient-to-r from-primary-500 to-primary-600 text-white rounded-lg hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? (
                  <>
                    <RefreshCw size={20} className="animate-spin" />
                    <span>Analyzing...</span>
                  </>
                ) : (
                  <>
                    <Rocket size={20} />
                    <span>Analyze Inbox</span>
                  </>
                )}
              </button>

              {selectedIds.length > 0 && (
                <button
                  onClick={handleDelete}
                  className="flex items-center gap-2 px-6 py-2 bg-red-50 text-red-600 rounded-lg hover:bg-red-100 transition-all"
                >
                  <Trash2 size={20} />
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
          <EmailTableModern
            emails={filteredEmails}
            selectedIds={selectedIds}
            onToggleSelect={handleToggleSelect}
            onToggleSelectAll={handleToggleSelectAll}
            onDelete={handleDelete}
            onArchive={handleArchive}
            searchQuery={searchQuery}
          />
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
        toastOptions={{
          style: {
            background: '#fff',
            color: '#171717',
            border: '1px solid #e5e5e5',
            boxShadow: '0 4px 12px rgba(0, 0, 0, 0.08)',
          },
        }}
      />
    </QueryClientProvider>
  );
}

export default App;

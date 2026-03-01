import { Mail, BarChart3, Settings, Search, Bell, X, CheckCircle, AlertCircle, Info, ChevronDown, Plus, Check, Inbox, PieChart } from 'lucide-react';
import { useState } from 'react';
import { createPortal } from 'react-dom';
import CardNav from './CardNav';
import LightPillar from './LightPillar';

export const Layout = ({ children, activeView, setActiveView, status, activeAccount, searchQuery, setSearchQuery, availableAccounts, onAccountSwitch, onAddAccount }) => {
  const [showNotifications, setShowNotifications] = useState(false);
  const [showAccountMenu, setShowAccountMenu] = useState(false);

  const notifications = [
    {
      id: 1,
      type: 'success',
      title: 'Emails Classified',
      message: '50 emails successfully analyzed',
      time: '2 minutes ago',
      read: false
    },
    {
      id: 2,
      type: 'info',
      title: 'Model Updated',
      message: 'TF-IDF classifier retrained with new data',
      time: '1 hour ago',
      read: false
    },
    {
      id: 3,
      type: 'warning',
      title: 'Low Confidence',
      message: '5 emails classified with <70% confidence',
      time: '3 hours ago',
      read: true
    }
  ];

  const unreadCount = notifications.filter(n => !n.read).length;

  const getNotificationIcon = (type) => {
    switch (type) {
      case 'success': return <CheckCircle size={18} className="text-green-400" />;
      case 'warning': return <AlertCircle size={18} className="text-amber-400" />;
      case 'info': return <Info size={18} className="text-blue-400" />;
      default: return <Info size={18} className="text-neutral-400" />;
    }
  };

  const cardNavItems = [
    {
      label: 'AI Summary',
      icon: '✨',
      bgColor: '#1e1e28',
      description: 'Get an instant overview of unread threads.',
      links: [
        { label: 'Summarize', ariaLabel: 'Summarize unread' },
        { label: 'Themes', ariaLabel: 'View common themes' },
      ],
    },
    {
      label: 'Priority Check',
      icon: '🎯',
      bgColor: '#1a2028',
      description: 'Identify high-value emails automatically.',
      links: [
        { label: 'Check now', ariaLabel: 'Check priority' },
        { label: 'Tuning', ariaLabel: 'Tune priority model' },
      ],
    },
    {
      label: 'Safety Sync',
      icon: '🛡️',
      bgColor: '#201e1a',
      description: 'Verify senders and check for phishing.',
      links: [
        { label: 'Verify', ariaLabel: 'Verify senders' },
        { label: 'Reports', ariaLabel: 'View safety report' },
      ],
    },
  ];

  const statusColor = status === 'Connected'
    ? 'bg-green-500/20 text-green-400 border-green-500/20'
    : status === 'Error'
      ? 'bg-red-500/20 text-red-400 border-red-500/20'
      : 'bg-amber-500/20 text-amber-400 border-amber-500/20';

  const statusDot = status === 'Connected'
    ? 'bg-green-400'
    : status === 'Error'
      ? 'bg-red-400'
      : 'bg-amber-400';

  return (
    <div className="flex h-screen bg-dark-950 relative overflow-hidden">
      {/* Ethereal Background Pillars */}
      <div className="app-background-pillar app-pillar-left">
        <LightPillar
          topColor="#a855f7"
          bottomColor="#ec4899"
          intensity={0.65}
          rotationSpeed={0.08}
          glowAmount={0.005}
          pillarWidth={2.5}
          pillarHeight={0.22}
          noiseIntensity={0.15}
          mixBlendMode="screen"
          pillarRotation={-20}
          quality="medium"
        />
      </div>
      <div className="app-background-pillar app-pillar-right">
        <LightPillar
          topColor="#3b82f6"
          bottomColor="#06b6d4"
          intensity={0.6}
          rotationSpeed={0.10}
          glowAmount={0.005}
          pillarWidth={2.3}
          pillarHeight={0.25}
          noiseIntensity={0.18}
          mixBlendMode="screen"
          pillarRotation={20}
          quality="medium"
        />
      </div>

      {/* Sidebar */}
      <aside className="w-72 bg-dark-900/40 backdrop-blur-xl border-r border-white/[0.04] flex flex-col z-10">
        {/* Logo */}
        <div className="p-5 border-b border-white/[0.04]">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 bg-gradient-to-br from-primary-500/80 to-primary-700/80 rounded-lg flex items-center justify-center text-lg">
              🤖
            </div>
            <div>
              <h1 className="font-semibold text-neutral-100 text-[15px] tracking-tight">EmailAI</h1>
              <p className="text-[11px] text-neutral-500">Smart Classifier</p>
            </div>
          </div>
        </div>

        {/* Quick Nav */}
        <nav className="p-4 space-y-0.5">
          <button
            onClick={() => setActiveView('inbox')}
            className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-[13px] transition-all ${activeView === 'inbox'
              ? 'bg-primary-500/10 text-primary-400 font-medium'
              : 'text-neutral-400 hover:bg-white/[0.03] hover:text-neutral-300'
              }`}
          >
            <Mail size={17} />
            <span>Inbox</span>
          </button>

          <button
            onClick={() => setActiveView('analytics')}
            className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-[13px] transition-all ${activeView === 'analytics'
              ? 'bg-primary-500/10 text-primary-400 font-medium'
              : 'text-neutral-400 hover:bg-white/[0.03] hover:text-neutral-300'
              }`}
          >
            <BarChart3 size={17} />
            <span>Analytics</span>
          </button>

          <button
            onClick={() => setActiveView('settings')}
            className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-[13px] transition-all ${activeView === 'settings'
              ? 'bg-primary-500/10 text-primary-400 font-medium'
              : 'text-neutral-400 hover:bg-white/[0.03] hover:text-neutral-300'
              }`}
          >
            <Settings size={17} />
            <span>Settings</span>
          </button>
        </nav>

        {/* Divider with label */}
        <div className="px-5 pt-2 pb-1">
          <p className="text-[10px] font-semibold text-neutral-600 uppercase tracking-widest">Smart Actions</p>
        </div>

        {/* CardNav */}
        <div className="px-4 pb-4">
          <CardNav
            items={cardNavItems}
            onNavigate={setActiveView}
            activeView={activeView}
          />
        </div>

        {/* Spacer */}
        <div className="flex-1" />

        {/* Connection Status */}
        <div className="px-4 pb-3">
          <div className={`flex items-center gap-2 px-3 py-2 rounded-lg border text-[12px] ${statusColor}`}>
            <div className={`w-1.5 h-1.5 rounded-full ${statusDot} ${status === 'Connected' ? 'animate-pulse' : ''}`} />
            <span className="font-medium">{status}</span>
          </div>
        </div>

        {/* User Profile */}
        <div className="p-4 border-t border-white/[0.04]">
          <div className="relative">
            <button
              onClick={() => setShowAccountMenu(!showAccountMenu)}
              className="w-full flex items-center gap-3 p-2.5 rounded-lg hover:bg-white/[0.03] cursor-pointer transition-all"
            >
              <div className="w-8 h-8 bg-gradient-to-br from-primary-500/70 to-primary-700/70 rounded-full flex items-center justify-center text-white text-sm font-semibold">
                {activeAccount.charAt(0).toUpperCase()}
              </div>
              <div className="flex-1 min-w-0 text-left">
                <p className="text-[13px] font-medium text-neutral-200 truncate">
                  {activeAccount === 'default' ? 'User' : activeAccount.split('@')[0]}
                </p>
                <p className="text-[11px] text-neutral-500 truncate">
                  {activeAccount === 'default' ? 'Default' : activeAccount}
                </p>
              </div>
              <ChevronDown size={14} className={`text-neutral-500 transition-transform ${showAccountMenu ? 'rotate-180' : ''}`} />
            </button>

            {/* Account Switcher */}
            {showAccountMenu && (
              <>
                <div
                  className="fixed inset-0 z-40"
                  onClick={() => setShowAccountMenu(false)}
                />

                <div className="absolute bottom-full left-0 right-0 mb-2 glass rounded-lg shadow-glass z-50 overflow-hidden">
                  <div className="p-2.5 border-b border-white/[0.06]">
                    <p className="text-[10px] font-semibold text-neutral-500 uppercase tracking-wider px-2">
                      Switch Account
                    </p>
                  </div>

                  <div className="max-h-48 overflow-y-auto">
                    {availableAccounts && availableAccounts.length > 0 ? (
                      availableAccounts.map((account) => (
                        <button
                          key={account}
                          onClick={() => {
                            onAccountSwitch(account);
                            setShowAccountMenu(false);
                          }}
                          className={`w-full flex items-center gap-3 p-2.5 hover:bg-white/[0.04] transition-all ${account === activeAccount ? 'bg-primary-500/5' : ''
                            }`}
                        >
                          <div className="w-7 h-7 bg-gradient-to-br from-primary-500/60 to-primary-700/60 rounded-full flex items-center justify-center text-white text-xs font-semibold">
                            {account.charAt(0).toUpperCase()}
                          </div>
                          <div className="flex-1 min-w-0 text-left">
                            <p className="text-[12px] font-medium text-neutral-200 truncate">
                              {account === 'default' ? 'Default Account' : account}
                            </p>
                          </div>
                          {account === activeAccount && (
                            <Check size={14} className="text-primary-400" />
                          )}
                        </button>
                      ))
                    ) : (
                      <div className="p-4 text-center text-[12px] text-neutral-500">
                        No accounts connected
                      </div>
                    )}
                  </div>

                  <div className="p-2 border-t border-white/[0.06]">
                    <button
                      onClick={() => {
                        onAddAccount();
                        setShowAccountMenu(false);
                      }}
                      className="w-full flex items-center gap-2 p-2.5 text-primary-400 hover:bg-primary-500/5 rounded-lg transition-all"
                    >
                      <Plus size={16} />
                      <span className="text-[12px] font-medium">Add Account</span>
                    </button>
                  </div>
                </div>
              </>
            )}
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden z-10">
        {/* Top Bar */}
        <header className="bg-dark-900/40 backdrop-blur-xl border-b border-white/[0.04] px-6 py-3">
          <div className="flex items-center justify-between">
            <div className="flex-1 max-w-lg">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-neutral-500" size={17} />
                <input
                  type="text"
                  placeholder="Search emails by subject or sender..."
                  value={searchQuery || ''}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-10 pr-10 py-2 bg-dark-800 border border-white/[0.06] rounded-lg text-[13px] text-neutral-200 placeholder-neutral-500 focus:outline-none focus:ring-1 focus:ring-primary-500/30 focus:border-primary-500/30 transition-all"
                />
                {searchQuery && (
                  <button
                    onClick={() => setSearchQuery('')}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-neutral-500 hover:text-neutral-300 transition-colors"
                  >
                    <X size={14} />
                  </button>
                )}
              </div>
            </div>

            <div className="flex items-center gap-3 ml-4">
              <div className="relative">
                <button
                  onClick={() => setShowNotifications(!showNotifications)}
                  className="relative p-2 text-neutral-400 hover:text-neutral-200 hover:bg-white/[0.04] rounded-lg transition-all"
                >
                  <Bell size={18} />
                  {unreadCount > 0 && (
                    <span className="absolute top-1 right-1 w-4 h-4 bg-primary-500 text-white text-[10px] font-bold rounded-full flex items-center justify-center">
                      {unreadCount}
                    </span>
                  )}
                </button>

                {/* Notifications Dropdown - Using Portal */}
                {showNotifications && createPortal(
                  <>
                    <div
                      className="fixed inset-0 z-[9998]"
                      onClick={() => setShowNotifications(false)}
                    />

                    <div 
                      className="fixed glass rounded-xl shadow-2xl z-[9999] overflow-hidden border border-violet-500/20 w-80"
                      style={{
                        top: '60px',
                        right: '24px'
                      }}
                    >
                      <div className="p-4 border-b border-white/[0.06] flex items-center justify-between bg-gradient-to-r from-violet-500/10 to-blue-500/10">
                        <h3 className="font-semibold text-neutral-100 text-sm">Notifications</h3>
                        <button
                          onClick={() => setShowNotifications(false)}
                          className="text-neutral-400 hover:text-neutral-200 transition-colors"
                        >
                          <X size={16} />
                        </button>
                      </div>

                      <div className="max-h-80 overflow-y-auto">
                        {notifications.length === 0 ? (
                          <div className="p-8 text-center">
                            <Bell size={40} className="mx-auto text-neutral-600 mb-3" />
                            <p className="text-neutral-500 text-sm">No notifications yet</p>
                          </div>
                        ) : (
                          <div className="divide-y divide-white/[0.04]">
                            {notifications.map(notification => (
                              <div
                                key={notification.id}
                                className={`p-3.5 hover:bg-white/[0.03] transition-all cursor-pointer ${!notification.read ? 'bg-violet-500/[0.05]' : ''
                                  }`}
                              >
                                <div className="flex gap-3">
                                  <div className="flex-shrink-0 mt-0.5">
                                    {getNotificationIcon(notification.type)}
                                  </div>
                                  <div className="flex-1 min-w-0">
                                    <div className="flex items-start justify-between gap-2">
                                      <p className="font-medium text-neutral-200 text-[13px]">
                                        {notification.title}
                                      </p>
                                      {!notification.read && (
                                        <span className="w-1.5 h-1.5 bg-violet-400 rounded-full flex-shrink-0 mt-1.5" />
                                      )}
                                    </div>
                                    <p className="text-[12px] text-neutral-400 mt-1">
                                      {notification.message}
                                    </p>
                                    <p className="text-[11px] text-neutral-600 mt-1.5">
                                      {notification.time}
                                    </p>
                                  </div>
                                </div>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>

                      {notifications.length > 0 && (
                        <div className="p-3 border-t border-white/[0.06] bg-gradient-to-r from-violet-500/5 to-blue-500/5">
                          <button className="w-full text-center text-[12px] text-violet-400 hover:text-violet-300 font-medium transition-colors">
                            Mark all as read
                          </button>
                        </div>
                      )}
                    </div>
                  </>,
                  document.body
                )}
              </div>
            </div>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 overflow-auto p-6">
          {children}
        </main>
      </div>
    </div>
  );
};

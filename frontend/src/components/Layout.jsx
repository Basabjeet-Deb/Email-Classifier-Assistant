import { Mail, BarChart3, Settings, LogOut, Search, Bell, X, CheckCircle, AlertCircle, Info, ChevronDown, Plus, Check } from 'lucide-react';
import { useState } from 'react';

export const Layout = ({ children, activeView, setActiveView, status, activeAccount, searchQuery, setSearchQuery, availableAccounts, onAccountSwitch, onAddAccount }) => {
  const [showNotifications, setShowNotifications] = useState(false);
  const [showAccountMenu, setShowAccountMenu] = useState(false);

  // Mock notifications - in production, these would come from backend
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
    switch(type) {
      case 'success': return <CheckCircle size={20} className="text-green-600" />;
      case 'warning': return <AlertCircle size={20} className="text-orange-600" />;
      case 'info': return <Info size={20} className="text-blue-600" />;
      default: return <Info size={20} className="text-neutral-600" />;
    }
  };

  return (
    <div className="flex h-screen bg-neutral-50">
      {/* Sidebar */}
      <aside className="w-64 bg-white border-r border-neutral-200 flex flex-col">
        {/* Logo */}
        <div className="p-6 border-b border-neutral-200">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-primary-400 to-primary-600 rounded-xl flex items-center justify-center text-white text-xl font-bold">
              🤖
            </div>
            <div>
              <h1 className="font-semibold text-neutral-900">EmailAI</h1>
              <p className="text-xs text-neutral-500">Smart Classifier</p>
            </div>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-4 space-y-1">
          <button
            onClick={() => setActiveView('inbox')}
            className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${
              activeView === 'inbox'
                ? 'bg-primary-50 text-primary-600 font-medium'
                : 'text-neutral-600 hover:bg-neutral-50'
            }`}
          >
            <Mail size={20} />
            <span>Inbox</span>
          </button>
          
          <button
            onClick={() => setActiveView('analytics')}
            className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${
              activeView === 'analytics'
                ? 'bg-primary-50 text-primary-600 font-medium'
                : 'text-neutral-600 hover:bg-neutral-50'
            }`}
          >
            <BarChart3 size={20} />
            <span>Analytics</span>
          </button>

          <button
            onClick={() => setActiveView('settings')}
            className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${
              activeView === 'settings'
                ? 'bg-primary-50 text-primary-600 font-medium'
                : 'text-neutral-600 hover:bg-neutral-50'
            }`}
          >
            <Settings size={20} />
            <span>Settings</span>
          </button>
        </nav>

        {/* User Profile */}
        <div className="p-4 border-t border-neutral-200">
          <div className="relative">
            <button
              onClick={() => setShowAccountMenu(!showAccountMenu)}
              className="w-full flex items-center gap-3 p-3 rounded-lg hover:bg-neutral-50 cursor-pointer transition-all"
            >
              <div className="w-10 h-10 bg-gradient-to-br from-primary-400 to-primary-600 rounded-full flex items-center justify-center text-white font-semibold">
                {activeAccount.charAt(0).toUpperCase()}
              </div>
              <div className="flex-1 min-w-0 text-left">
                <p className="text-sm font-medium text-neutral-900 truncate">
                  {activeAccount === 'default' ? 'User' : activeAccount.split('@')[0]}
                </p>
                <p className="text-xs text-neutral-500">{status}</p>
              </div>
              <ChevronDown size={16} className={`text-neutral-400 transition-transform ${showAccountMenu ? 'rotate-180' : ''}`} />
            </button>

            {/* Account Switcher Dropdown */}
            {showAccountMenu && (
              <>
                {/* Backdrop */}
                <div 
                  className="fixed inset-0 z-40" 
                  onClick={() => setShowAccountMenu(false)}
                />
                
                {/* Dropdown Menu */}
                <div className="absolute bottom-full left-4 right-4 mb-2 bg-white rounded-lg shadow-lg border border-neutral-200 z-50 overflow-hidden">
                  <div className="p-2 border-b border-neutral-200">
                    <p className="text-xs font-semibold text-neutral-500 uppercase tracking-wider px-3 py-2">
                      Switch Account
                    </p>
                  </div>

                  <div className="max-h-64 overflow-y-auto">
                    {availableAccounts && availableAccounts.length > 0 ? (
                      availableAccounts.map((account) => (
                        <button
                          key={account}
                          onClick={() => {
                            onAccountSwitch(account);
                            setShowAccountMenu(false);
                          }}
                          className={`w-full flex items-center gap-3 p-3 hover:bg-neutral-50 transition-all ${
                            account === activeAccount ? 'bg-primary-50' : ''
                          }`}
                        >
                          <div className="w-8 h-8 bg-gradient-to-br from-primary-400 to-primary-600 rounded-full flex items-center justify-center text-white text-sm font-semibold">
                            {account.charAt(0).toUpperCase()}
                          </div>
                          <div className="flex-1 min-w-0 text-left">
                            <p className="text-sm font-medium text-neutral-900 truncate">
                              {account === 'default' ? 'Default Account' : account}
                            </p>
                          </div>
                          {account === activeAccount && (
                            <Check size={16} className="text-primary-600" />
                          )}
                        </button>
                      ))
                    ) : (
                      <div className="p-4 text-center text-sm text-neutral-500">
                        No accounts connected
                      </div>
                    )}
                  </div>

                  <div className="p-2 border-t border-neutral-200">
                    <button
                      onClick={() => {
                        onAddAccount();
                        setShowAccountMenu(false);
                      }}
                      className="w-full flex items-center gap-2 p-3 text-primary-600 hover:bg-primary-50 rounded-lg transition-all"
                    >
                      <Plus size={18} />
                      <span className="text-sm font-medium">Add Account</span>
                    </button>
                  </div>
                </div>
              </>
            )}
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top Bar */}
        <header className="bg-white border-b border-neutral-200 px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex-1 max-w-xl">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-neutral-400" size={20} />
                <input
                  type="text"
                  placeholder="Search emails by subject or sender..."
                  value={searchQuery || ''}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-10 pr-10 py-2 bg-neutral-50 border border-neutral-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
                {searchQuery && (
                  <button
                    onClick={() => setSearchQuery('')}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-neutral-400 hover:text-neutral-600 transition-colors"
                  >
                    <X size={16} />
                  </button>
                )}
              </div>
            </div>
            
            <div className="flex items-center gap-4">
              <div className="relative">
                <button 
                  onClick={() => setShowNotifications(!showNotifications)}
                  className="relative p-2 text-neutral-600 hover:bg-neutral-50 rounded-lg transition-all"
                >
                  <Bell size={20} />
                  {unreadCount > 0 && (
                    <span className="absolute top-1 right-1 w-5 h-5 bg-primary-500 text-white text-xs font-bold rounded-full flex items-center justify-center">
                      {unreadCount}
                    </span>
                  )}
                </button>

                {/* Notifications Dropdown */}
                {showNotifications && (
                  <>
                    {/* Backdrop */}
                    <div 
                      className="fixed inset-0 z-40" 
                      onClick={() => setShowNotifications(false)}
                    />
                    
                    {/* Dropdown Panel */}
                    <div className="absolute right-0 mt-2 w-96 bg-white rounded-xl shadow-lg border border-neutral-200 z-50 overflow-hidden">
                      <div className="p-4 border-b border-neutral-200 flex items-center justify-between">
                        <h3 className="font-semibold text-neutral-900">Notifications</h3>
                        <button
                          onClick={() => setShowNotifications(false)}
                          className="text-neutral-400 hover:text-neutral-600"
                        >
                          <X size={18} />
                        </button>
                      </div>

                      <div className="max-h-96 overflow-y-auto">
                        {notifications.length === 0 ? (
                          <div className="p-8 text-center">
                            <Bell size={48} className="mx-auto text-neutral-300 mb-3" />
                            <p className="text-neutral-500">No notifications yet</p>
                          </div>
                        ) : (
                          <div className="divide-y divide-neutral-100">
                            {notifications.map(notification => (
                              <div
                                key={notification.id}
                                className={`p-4 hover:bg-neutral-50 transition-all cursor-pointer ${
                                  !notification.read ? 'bg-primary-50/30' : ''
                                }`}
                              >
                                <div className="flex gap-3">
                                  <div className="flex-shrink-0 mt-1">
                                    {getNotificationIcon(notification.type)}
                                  </div>
                                  <div className="flex-1 min-w-0">
                                    <div className="flex items-start justify-between gap-2">
                                      <p className="font-medium text-neutral-900 text-sm">
                                        {notification.title}
                                      </p>
                                      {!notification.read && (
                                        <span className="w-2 h-2 bg-primary-500 rounded-full flex-shrink-0 mt-1.5" />
                                      )}
                                    </div>
                                    <p className="text-sm text-neutral-600 mt-1">
                                      {notification.message}
                                    </p>
                                    <p className="text-xs text-neutral-400 mt-2">
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
                        <div className="p-3 border-t border-neutral-200 bg-neutral-50">
                          <button className="w-full text-center text-sm text-primary-600 hover:text-primary-700 font-medium">
                            Mark all as read
                          </button>
                        </div>
                      )}
                    </div>
                  </>
                )}
              </div>
            </div>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 overflow-auto p-8">
          {children}
        </main>
      </div>
    </div>
  );
};

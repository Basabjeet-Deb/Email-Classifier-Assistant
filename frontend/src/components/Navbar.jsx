import { Search, Bell, X, CheckCircle, AlertCircle, Info } from 'lucide-react';
import { useState } from 'react';
import { createPortal } from 'react-dom';

export const Navbar = ({ searchQuery, setSearchQuery }) => {
  const [showNotifications, setShowNotifications] = useState(false);

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

  return (
    <header className="bg-dark-900/40 backdrop-blur-xl border-b border-white/[0.04] px-6 py-3.5 sticky top-0 z-50">
      <div className="flex items-center justify-between gap-6">
        {/* Centered Search Bar */}
        <div className="flex-1 max-w-2xl mx-auto">
          <div className="relative">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-neutral-500" size={18} />
            <input
              type="text"
              placeholder="Search emails by sender, subject, or keywords..."
              value={searchQuery || ''}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-12 pr-12 py-2.5 bg-dark-800/60 border border-white/[0.08] rounded-xl text-[13px] text-neutral-200 placeholder-neutral-500 focus:outline-none focus:ring-2 focus:ring-primary-500/40 focus:border-primary-500/40 transition-all"
            />
            {searchQuery && (
              <button
                onClick={() => setSearchQuery('')}
                className="absolute right-4 top-1/2 -translate-y-1/2 text-neutral-500 hover:text-neutral-300 transition-colors"
              >
                <X size={16} />
              </button>
            )}
          </div>
        </div>

        {/* Right Actions */}
        <div className="flex items-center gap-2">
          <div className="relative">
            <button
              onClick={() => setShowNotifications(!showNotifications)}
              className="relative p-2.5 text-neutral-400 hover:text-neutral-200 hover:bg-white/[0.04] rounded-xl transition-all"
            >
              <Bell size={19} />
              {unreadCount > 0 && (
                <span className="absolute top-1.5 right-1.5 w-4 h-4 bg-primary-500 text-white text-[9px] font-bold rounded-full flex items-center justify-center">
                  {unreadCount}
                </span>
              )}
            </button>

            {/* Notifications Dropdown */}
            {showNotifications && createPortal(
              <>
                <div
                  className="fixed inset-0 z-[9998]"
                  onClick={() => setShowNotifications(false)}
                />

                <div 
                  className="fixed glass rounded-xl shadow-2xl z-[9999] overflow-hidden border border-violet-500/20 w-80"
                  style={{
                    top: '70px',
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
                            className={`p-3.5 hover:bg-white/[0.03] transition-all cursor-pointer ${!notification.read ? 'bg-violet-500/[0.05]' : ''}`}
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

          {/* User Avatar */}
          <div className="w-9 h-9 bg-gradient-to-br from-primary-500/70 to-primary-700/70 rounded-full flex items-center justify-center text-white text-sm font-semibold">
            U
          </div>
        </div>
      </div>
    </header>
  );
};

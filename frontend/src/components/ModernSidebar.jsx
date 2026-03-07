import { Mail, BarChart3, Settings, ChevronDown, Plus, Check, Sparkles, Target, Shield } from 'lucide-react';
import { useState } from 'react';

export const ModernSidebar = ({ 
  activeView, 
  setActiveView, 
  status, 
  activeAccount, 
  availableAccounts, 
  onAccountSwitch, 
  onAddAccount 
}) => {
  const [showAccountMenu, setShowAccountMenu] = useState(false);

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

  const navItems = [
    { id: 'inbox', label: 'Inbox', icon: Mail },
    { id: 'analytics', label: 'Analytics', icon: BarChart3 },
    { id: 'settings', label: 'Settings', icon: Settings },
  ];

  const smartActions = [
    {
      id: 'ai-summary',
      label: 'AI Summary',
      icon: Sparkles,
      description: 'Get instant overview',
      color: 'from-violet-500/10 to-purple-500/10',
      iconColor: 'text-violet-400',
    },
    {
      id: 'priority-check',
      label: 'Priority Check',
      icon: Target,
      description: 'Find important emails',
      color: 'from-blue-500/10 to-cyan-500/10',
      iconColor: 'text-blue-400',
    },
    {
      id: 'safety-sync',
      label: 'Safety Sync',
      icon: Shield,
      description: 'Verify senders',
      color: 'from-emerald-500/10 to-green-500/10',
      iconColor: 'text-emerald-400',
    },
  ];

  return (
    <aside className="w-72 bg-dark-900/40 backdrop-blur-xl border-r border-white/[0.04] flex flex-col">
      {/* Logo */}
      <div className="p-5 border-b border-white/[0.04]">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-br from-primary-500/80 to-primary-700/80 rounded-xl flex items-center justify-center text-xl shadow-lg">
            🤖
          </div>
          <div>
            <h1 className="font-bold text-neutral-100 text-[16px] tracking-tight">EmailAI</h1>
            <p className="text-[11px] text-neutral-500">Smart Classifier</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="p-4 space-y-1">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeView === item.id;
          
          return (
            <button
              key={item.id}
              onClick={() => setActiveView(item.id)}
              className={`sidebar-item w-full flex items-center gap-3 px-4 py-3 rounded-xl text-[13.5px] font-medium transition-all ${
                isActive
                  ? 'bg-primary-500/10 text-primary-400'
                  : 'text-neutral-400 hover:text-neutral-300'
              }`}
            >
              <Icon size={18} />
              <span>{item.label}</span>
            </button>
          );
        })}
      </nav>

      {/* Smart Actions */}
      <div className="px-4 pt-2 pb-4">
        <p className="text-[10px] font-semibold text-neutral-600 uppercase tracking-widest px-4 mb-3">
          Smart Actions
        </p>
        <div className="space-y-2">
          {smartActions.map((action) => {
            const Icon = action.icon;
            
            return (
              <button
                key={action.id}
                className={`w-full p-3 rounded-xl bg-gradient-to-br ${action.color} border border-white/[0.05] hover:border-white/[0.1] transition-all group`}
              >
                <div className="flex items-center gap-3">
                  <div className={`w-8 h-8 rounded-lg bg-dark-800/50 flex items-center justify-center ${action.iconColor}`}>
                    <Icon size={16} />
                  </div>
                  <div className="flex-1 text-left">
                    <p className="text-[12px] font-semibold text-neutral-200">{action.label}</p>
                    <p className="text-[10px] text-neutral-500">{action.description}</p>
                  </div>
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Spacer */}
      <div className="flex-1" />

      {/* Connection Status */}
      <div className="px-4 pb-3">
        <div className={`flex items-center gap-2.5 px-4 py-2.5 rounded-xl border text-[12px] font-medium ${statusColor}`}>
          <div className={`w-2 h-2 rounded-full ${statusDot} ${status === 'Connected' ? 'animate-pulse' : ''}`} />
          <span>{status}</span>
        </div>
      </div>

      {/* User Profile */}
      <div className="p-4 border-t border-white/[0.04]">
        <div className="relative">
          <button
            onClick={() => setShowAccountMenu(!showAccountMenu)}
            className="w-full flex items-center gap-3 p-3 rounded-xl hover:bg-white/[0.03] cursor-pointer transition-all"
          >
            <div className="w-9 h-9 bg-gradient-to-br from-primary-500/70 to-primary-700/70 rounded-full flex items-center justify-center text-white text-sm font-semibold shadow-lg">
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
            <ChevronDown size={16} className={`text-neutral-500 transition-transform ${showAccountMenu ? 'rotate-180' : ''}`} />
          </button>

          {/* Account Switcher */}
          {showAccountMenu && (
            <>
              <div
                className="fixed inset-0 z-40"
                onClick={() => setShowAccountMenu(false)}
              />

              <div className="absolute bottom-full left-0 right-0 mb-2 glass rounded-xl shadow-glass z-50 overflow-hidden border border-white/[0.08]">
                <div className="p-3 border-b border-white/[0.06]">
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
                        className={`w-full flex items-center gap-3 p-3 hover:bg-white/[0.04] transition-all ${
                          account === activeAccount ? 'bg-primary-500/5' : ''
                        }`}
                      >
                        <div className="w-8 h-8 bg-gradient-to-br from-primary-500/60 to-primary-700/60 rounded-full flex items-center justify-center text-white text-xs font-semibold">
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
  );
};

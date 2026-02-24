import { Mail, BarChart3 } from 'lucide-react';

export const Header = ({ activeView, setActiveView, status, activeAccount }) => {
  return (
    <header className="sticky top-0 z-50 bg-white/80 backdrop-blur-xl border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          {/* Logo */}
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-primary-600 rounded-xl flex items-center justify-center text-white text-xl">
              🤖
            </div>
            <span className="text-xl font-semibold text-gray-900">AI Email Classifier</span>
          </div>

          {/* Navigation */}
          <div className="flex items-center gap-2 bg-gray-100 p-1 rounded-xl">
            <button
              onClick={() => setActiveView('inbox')}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-all ${
                activeView === 'inbox'
                  ? 'bg-white text-primary-600 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <Mail size={18} />
              <span>Inbox</span>
            </button>
            <button
              onClick={() => setActiveView('analytics')}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-all ${
                activeView === 'analytics'
                  ? 'bg-white text-primary-600 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <BarChart3 size={18} />
              <span>Analytics</span>
            </button>
          </div>

          {/* Status */}
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 px-3 py-1.5 bg-green-50 border border-green-200 rounded-full">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
              <span className="text-sm font-medium text-green-700">{status}</span>
            </div>
            <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-primary-600 rounded-full flex items-center justify-center text-white font-semibold">
              {activeAccount.charAt(0).toUpperCase()}
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};

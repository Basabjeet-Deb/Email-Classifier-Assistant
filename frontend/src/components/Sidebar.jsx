import { Rocket, Trash2 } from 'lucide-react';

export const Sidebar = ({ 
  onScan, 
  onDelete, 
  loading, 
  selectedCount,
  totalScanned,
  avgConfidence,
  scanLimit,
  setScanLimit,
  scanType,
  setScanType
}) => {
  return (
    <div className="space-y-4">
      {/* Scan Control */}
      <div className="glass rounded-2xl p-6">
        <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-4">
          Scan Control
        </h3>
        
        <button
          onClick={onScan}
          disabled={loading}
          className="w-full bg-gradient-to-r from-primary-500 to-primary-600 text-white px-6 py-3 rounded-xl font-medium hover:shadow-lg hover:-translate-y-0.5 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
        >
          {loading ? (
            <>
              <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              <span>Analyzing...</span>
            </>
          ) : (
            <>
              <Rocket size={20} />
              <span>Analyze Inbox</span>
            </>
          )}
        </button>

        <div className="mt-4 space-y-3">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Fetch Limit
            </label>
            <select
              value={scanLimit}
              onChange={(e) => setScanLimit(Number(e.target.value))}
              className="w-full px-4 py-2 bg-white border border-gray-200 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
            >
              <option value={10}>10 Messages</option>
              <option value={50}>50 Messages</option>
              <option value={100}>100 Messages</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Target Category
            </label>
            <select
              value={scanType}
              onChange={(e) => setScanType(e.target.value)}
              className="w-full px-4 py-2 bg-white border border-gray-200 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
            >
              <option value="in:inbox category:promotions OR is:unread">Promos & Unread</option>
              <option value="is:unread">Unread Only</option>
              <option value="category:promotions">All Promotions</option>
            </select>
          </div>
        </div>
      </div>

      {/* Statistics */}
      <div className="glass rounded-2xl p-6">
        <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-4">
          Statistics
        </h3>
        <div className="grid grid-cols-2 gap-3">
          <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl p-4 border border-blue-200">
            <div className="text-2xl font-bold text-blue-900">{totalScanned}</div>
            <div className="text-xs text-blue-600 uppercase tracking-wide">Scanned</div>
          </div>
          <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-xl p-4 border border-purple-200">
            <div className="text-2xl font-bold text-purple-900">{avgConfidence}%</div>
            <div className="text-xs text-purple-600 uppercase tracking-wide">Confidence</div>
          </div>
        </div>
      </div>

      {/* Delete Control */}
      <div className="glass rounded-2xl p-6">
        <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-4">
          Actions
        </h3>
        <button
          onClick={onDelete}
          disabled={selectedCount === 0}
          className="w-full bg-gradient-to-r from-red-500 to-red-600 text-white px-6 py-3 rounded-xl font-medium hover:shadow-lg hover:-translate-y-0.5 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
        >
          <Trash2 size={20} />
          <span>Delete ({selectedCount})</span>
        </button>
      </div>

      {/* ML Info */}
      <div className="glass rounded-2xl p-6">
        <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-4">
          ML System
        </h3>
        <div className="space-y-3">
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-600">Classifier</span>
            <span className="text-sm font-semibold text-primary-600">TF-IDF</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-600">Categories</span>
            <span className="text-sm font-semibold text-primary-600">5</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-600">Method</span>
            <span className="text-sm font-semibold text-primary-600">Ensemble</span>
          </div>
        </div>
      </div>
    </div>
  );
};

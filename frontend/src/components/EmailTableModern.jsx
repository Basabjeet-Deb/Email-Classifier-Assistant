import { useState } from 'react';
import { Lock, MoreVertical, Trash2, Archive, Tag } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const getCategoryColor = (category) => {
  const colors = {
    'Banking/Financial': 'bg-green-100 text-green-700 border-green-200',
    'Shopping/Orders': 'bg-blue-100 text-blue-700 border-blue-200',
    'Work/Career': 'bg-teal-100 text-teal-700 border-teal-200',
    'Promotional': 'bg-orange-100 text-orange-700 border-orange-200',
    'Personal/Other': 'bg-neutral-100 text-neutral-700 border-neutral-200',
  };
  return colors[category] || 'bg-neutral-100 text-neutral-700 border-neutral-200';
};

const isProtected = (category) => {
  return ['Banking/Financial', 'Work/Career', 'Shopping/Orders'].some(c => category.includes(c));
};

export const EmailTableModern = ({ emails, selectedIds, onToggleSelect, onToggleSelectAll, onDelete, onArchive, searchQuery }) => {
  const [selectedEmail, setSelectedEmail] = useState(null);
  const [filterCategory, setFilterCategory] = useState('all');

  const allSelected = emails.length > 0 && selectedIds.length === emails.filter(e => !isProtected(e.category)).length;

  const filteredEmails = filterCategory === 'all' 
    ? emails 
    : emails.filter(e => e.category === filterCategory);

  const categories = ['all', ...new Set(emails.map(e => e.category))];

  if (emails.length === 0) {
    return (
      <div className="bg-white rounded-xl p-12 text-center shadow-card border border-neutral-200">
        <div className="text-6xl mb-4">📧</div>
        <h3 className="text-xl font-semibold text-neutral-900 mb-2">No emails to display</h3>
        <p className="text-neutral-500">
          {searchQuery 
            ? `No emails match "${searchQuery}". Try a different search term.`
            : 'Click "Analyze Inbox" to start classifying your emails'
          }
        </p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Email List */}
      <div className="lg:col-span-2">
        <div className="bg-white rounded-xl shadow-card border border-neutral-200 overflow-hidden">
          {/* Filters */}
          <div className="p-4 border-b border-neutral-200">
            <div className="flex items-center justify-between mb-2">
              <p className="text-sm font-medium text-neutral-700">Filter by category</p>
              {filterCategory !== 'all' && (
                <button
                  onClick={() => setFilterCategory('all')}
                  className="text-xs text-primary-600 hover:text-primary-700 font-medium"
                >
                  Clear filter
                </button>
              )}
            </div>
            <div className="flex items-center gap-2 overflow-x-auto">
              {categories.map(cat => (
                <button
                  key={cat}
                  onClick={() => setFilterCategory(cat)}
                  className={`px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-all ${
                    filterCategory === cat
                      ? 'bg-primary-100 text-primary-700'
                      : 'bg-neutral-50 text-neutral-600 hover:bg-neutral-100'
                  }`}
                >
                  {cat === 'all' ? `All (${emails.length})` : `${cat} (${emails.filter(e => e.category === cat).length})`}
                </button>
              ))}
            </div>
          </div>

          {/* Table Header */}
          <div className="px-6 py-3 bg-neutral-50 border-b border-neutral-200 flex items-center gap-4 text-xs font-semibold text-neutral-500 uppercase tracking-wider">
            <input
              type="checkbox"
              checked={allSelected}
              onChange={onToggleSelectAll}
              className="w-4 h-4 text-primary-600 rounded focus:ring-2 focus:ring-primary-500"
            />
            <div className="flex-1">Email</div>
            <div className="w-32">Category</div>
            <div className="w-20">Confidence</div>
            <div className="w-10"></div>
          </div>

          {/* Email List */}
          <div className="divide-y divide-neutral-100 max-h-[600px] overflow-y-auto">
            {filteredEmails.map((email, index) => {
              const isEmailProtected = isProtected(email.category);
              const selected = selectedIds.includes(email.id);
              const confidence = Math.round((email.confidence || 0) * 100);
              const isActive = selectedEmail?.id === email.id;

              return (
                <motion.div
                  key={email.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.03 }}
                  className={`px-6 py-4 flex items-center gap-4 hover:bg-neutral-50 cursor-pointer transition-all ${
                    isActive ? 'bg-primary-50' : ''
                  }`}
                  onClick={() => setSelectedEmail(email)}
                >
                  <div onClick={(e) => e.stopPropagation()}>
                    {isEmailProtected ? (
                      <Lock size={16} className="text-neutral-400" />
                    ) : (
                      <input
                        type="checkbox"
                        checked={selected}
                        onChange={() => onToggleSelect(email.id)}
                        className="w-4 h-4 text-primary-600 rounded focus:ring-2 focus:ring-primary-500"
                      />
                    )}
                  </div>

                  <div className="flex-1 min-w-0">
                    <p className="font-medium text-neutral-900 truncate">{email.subject || '(No Subject)'}</p>
                    <p className="text-sm text-neutral-500 truncate">{email.sender.split('<')[0]}</p>
                  </div>

                  <span className={`px-3 py-1 rounded-lg text-xs font-semibold border ${getCategoryColor(email.category)}`}>
                    {email.category}
                  </span>

                  <div className="w-20">
                    <div className="flex items-center gap-2">
                      <div className="flex-1 h-1.5 bg-neutral-200 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-gradient-to-r from-primary-400 to-primary-600 transition-all duration-500"
                          style={{ width: `${confidence}%` }}
                        />
                      </div>
                      <span className="text-xs font-medium text-neutral-600">{confidence}%</span>
                    </div>
                  </div>

                  <button className="p-1 hover:bg-neutral-100 rounded transition-all">
                    <MoreVertical size={16} className="text-neutral-400" />
                  </button>
                </motion.div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Email Preview */}
      <div className="lg:col-span-1">
        <AnimatePresence mode="wait">
          {selectedEmail ? (
            <motion.div
              key={selectedEmail.id}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              className="bg-white rounded-xl shadow-card border border-neutral-200 p-6 sticky top-0"
            >
              <div className="flex items-start justify-between mb-4">
                <h3 className="font-semibold text-neutral-900">Email Preview</h3>
                <button
                  onClick={() => setSelectedEmail(null)}
                  className="text-neutral-400 hover:text-neutral-600"
                >
                  ✕
                </button>
              </div>

              <div className="space-y-4">
                <div>
                  <p className="text-xs text-neutral-500 mb-1">Subject</p>
                  <p className="font-medium text-neutral-900">{selectedEmail.subject || '(No Subject)'}</p>
                </div>

                <div>
                  <p className="text-xs text-neutral-500 mb-1">From</p>
                  <p className="text-sm text-neutral-700">{selectedEmail.sender}</p>
                </div>

                <div>
                  <p className="text-xs text-neutral-500 mb-1">Category</p>
                  <span className={`inline-block px-3 py-1 rounded-lg text-xs font-semibold border ${getCategoryColor(selectedEmail.category)}`}>
                    {selectedEmail.category}
                  </span>
                </div>

                <div>
                  <p className="text-xs text-neutral-500 mb-1">Confidence</p>
                  <div className="flex items-center gap-2">
                    <div className="flex-1 h-2 bg-neutral-200 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-gradient-to-r from-primary-400 to-primary-600"
                        style={{ width: `${Math.round((selectedEmail.confidence || 0) * 100)}%` }}
                      />
                    </div>
                    <span className="text-sm font-medium text-neutral-900">
                      {Math.round((selectedEmail.confidence || 0) * 100)}%
                    </span>
                  </div>
                </div>

                <div>
                  <p className="text-xs text-neutral-500 mb-2">Preview</p>
                  <p className="text-sm text-neutral-600 leading-relaxed">{selectedEmail.snippet}</p>
                </div>

                {!isProtected(selectedEmail.category) && (
                  <div className="pt-4 border-t border-neutral-200 flex gap-2">
                    <button
                      onClick={() => {
                        if (!selectedIds.includes(selectedEmail.id)) {
                          onToggleSelect(selectedEmail.id);
                        }
                        setTimeout(() => onDelete(), 100);
                      }}
                      className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-red-50 text-red-600 rounded-lg hover:bg-red-100 transition-all"
                    >
                      <Trash2 size={16} />
                      <span>Delete</span>
                    </button>
                    <button 
                      onClick={() => onArchive && onArchive(selectedEmail.id)}
                      className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-neutral-50 text-neutral-600 rounded-lg hover:bg-neutral-100 transition-all"
                    >
                      <Archive size={16} />
                      <span>Archive</span>
                    </button>
                  </div>
                )}
              </div>
            </motion.div>
          ) : (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="bg-white rounded-xl shadow-card border border-neutral-200 p-12 text-center"
            >
              <div className="text-4xl mb-4">👆</div>
              <p className="text-neutral-500">Select an email to preview</p>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};

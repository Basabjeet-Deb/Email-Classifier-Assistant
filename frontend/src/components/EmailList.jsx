import { useState } from 'react';
import { Lock, ChevronDown, ChevronRight } from 'lucide-react';
import { motion } from 'framer-motion';

const getCategoryColor = (category) => {
  const colors = {
    'Important': 'bg-red-500/15 text-red-400 border-red-500/20',
    'Transactional': 'bg-blue-500/15 text-blue-400 border-blue-500/20',
    'Promotional': 'bg-amber-500/15 text-amber-400 border-amber-500/20',
    'Social': 'bg-cyan-500/15 text-cyan-400 border-cyan-500/20',
    'Spam': 'bg-neutral-500/15 text-neutral-400 border-neutral-500/20',
  };
  return colors[category] || 'bg-neutral-500/15 text-neutral-400 border-neutral-500/20';
};

const isProtected = (category) => {
  return ['Important', 'Transactional'].includes(category);
};

export const EmailList = ({ 
  emails, 
  selectedIds, 
  onToggleSelect, 
  selectedEmail, 
  setSelectedEmail,
  filterCategory,
  setFilterCategory 
}) => {
  const [collapsedCategories, setCollapsedCategories] = useState({});

  const filteredEmails = filterCategory === 'all'
    ? emails
    : emails.filter(e => e.category === filterCategory);

  const categories = ['all', ...new Set(emails.map(e => e.category))];

  // Group emails by category
  const emailsByCategory = filteredEmails.reduce((acc, email) => {
    if (!acc[email.category]) {
      acc[email.category] = [];
    }
    acc[email.category].push(email);
    return acc;
  }, {});

  const toggleCategory = (category) => {
    setCollapsedCategories(prev => ({
      ...prev,
      [category]: !prev[category]
    }));
  };

  const formatTime = (dateString) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
  };

  if (emails.length === 0) {
    return (
      <div className="glass rounded-xl p-16 text-center border border-violet-500/20 relative overflow-hidden">
        <div className="absolute inset-0 opacity-30">
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-64 h-64 bg-violet-500/20 rounded-full blur-3xl animate-pulse" />
        </div>
        
        <div className="relative z-10">
          <div className="w-20 h-20 mx-auto mb-6 bg-gradient-to-br from-violet-500/20 to-blue-500/20 rounded-2xl flex items-center justify-center border border-violet-500/30">
            <span className="text-5xl">📧</span>
          </div>
          <h3 className="text-xl font-bold text-neutral-100 mb-3">No emails to display</h3>
          <p className="text-neutral-400 text-sm max-w-md mx-auto leading-relaxed">
            Click "Analyze Inbox" to start classifying your emails with AI-powered intelligence
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="glass rounded-xl overflow-hidden border border-white/[0.06]">
      {/* Filters */}
      <div className="p-4 border-b border-white/[0.04] bg-dark-800/30">
        <div className="flex items-center justify-between mb-2">
          <p className="text-xs font-medium text-neutral-400">Filter by category</p>
          {filterCategory !== 'all' && (
            <button
              onClick={() => setFilterCategory('all')}
              className="text-[11px] text-primary-400 hover:text-primary-300 font-medium transition-colors"
            >
              Clear filter
            </button>
          )}
        </div>
        <div className="flex items-center gap-2 overflow-x-auto pb-1">
          {categories.map(cat => (
            <button
              key={cat}
              onClick={() => setFilterCategory(cat)}
              className={`px-3 py-1.5 rounded-lg text-[12px] font-medium whitespace-nowrap transition-all ${
                filterCategory === cat
                  ? 'bg-primary-500/15 text-primary-400 border border-primary-500/30'
                  : 'bg-white/[0.03] text-neutral-500 hover:bg-white/[0.06] hover:text-neutral-300 border border-transparent'
              }`}
            >
              {cat === 'all' ? `All (${emails.length})` : `${cat} (${emails.filter(e => e.category === cat).length})`}
            </button>
          ))}
        </div>
      </div>

      {/* Email List - Grouped by Category */}
      <div className="max-h-[calc(100vh-280px)] overflow-y-auto">
        {filterCategory === 'all' ? (
          // Grouped view
          Object.entries(emailsByCategory).map(([category, categoryEmails]) => (
            <div key={category} className="border-b border-white/[0.03] last:border-b-0">
              {/* Category Header */}
              <button
                onClick={() => toggleCategory(category)}
                className="w-full px-5 py-3 bg-dark-800/20 hover:bg-dark-800/30 transition-all flex items-center justify-between"
              >
                <div className="flex items-center gap-3">
                  {collapsedCategories[category] ? (
                    <ChevronRight size={16} className="text-neutral-500" />
                  ) : (
                    <ChevronDown size={16} className="text-neutral-500" />
                  )}
                  <span className={`px-2.5 py-1 rounded-md text-[11px] font-semibold border ${getCategoryColor(category)}`}>
                    {category}
                  </span>
                  <span className="text-[12px] text-neutral-500">
                    {categoryEmails.length} email{categoryEmails.length !== 1 ? 's' : ''}
                  </span>
                </div>
              </button>

              {/* Category Emails */}
              {!collapsedCategories[category] && (
                <div className="divide-y divide-white/[0.02]">
                  {categoryEmails.map((email, index) => {
                    const isEmailProtected = isProtected(email.category);
                    const selected = selectedIds.includes(email.id);
                    const isActive = selectedEmail?.id === email.id;

                    return (
                      <motion.div
                        key={email.id}
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: index * 0.02 }}
                        className={`email-row px-5 py-3.5 flex items-center gap-4 ${
                          isActive ? 'bg-primary-500/[0.08] active' : ''
                        }`}
                        onClick={() => setSelectedEmail(email)}
                      >
                        <div onClick={(e) => e.stopPropagation()}>
                          {isEmailProtected ? (
                            <Lock size={14} className="text-neutral-600" />
                          ) : (
                            <input
                              type="checkbox"
                              checked={selected}
                              onChange={() => onToggleSelect(email.id)}
                              className="w-3.5 h-3.5 rounded accent-primary-500"
                            />
                          )}
                        </div>

                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-1">
                            <p className="text-[13px] font-medium text-neutral-200 truncate flex-1">
                              {email.sender.split('<')[0].trim() || email.sender}
                            </p>
                            <span className="text-[11px] text-neutral-600 flex-shrink-0">
                              {formatTime(email.date)}
                            </span>
                          </div>
                          <p className="text-[12px] text-neutral-400 truncate">
                            {email.subject || '(No Subject)'}
                          </p>
                          <p className="text-[11px] text-neutral-600 truncate mt-0.5">
                            {email.snippet}
                          </p>
                        </div>

                        <div className="flex items-center gap-2 flex-shrink-0">
                          <div className="w-16">
                            <div className="h-1 bg-white/[0.06] rounded-full overflow-hidden">
                              <div
                                className="h-full bg-gradient-to-r from-primary-500/70 to-primary-400/70 transition-all duration-500"
                                style={{ width: `${Math.round((email.confidence || 0) * 100)}%` }}
                              />
                            </div>
                          </div>
                        </div>
                      </motion.div>
                    );
                  })}
                </div>
              )}
            </div>
          ))
        ) : (
          // Flat view when filtered
          <div className="divide-y divide-white/[0.02]">
            {filteredEmails.map((email, index) => {
              const isEmailProtected = isProtected(email.category);
              const selected = selectedIds.includes(email.id);
              const isActive = selectedEmail?.id === email.id;

              return (
                <motion.div
                  key={email.id}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: index * 0.02 }}
                  className={`email-row px-5 py-3.5 flex items-center gap-4 ${
                    isActive ? 'bg-primary-500/[0.08] active' : ''
                  }`}
                  onClick={() => setSelectedEmail(email)}
                >
                  <div onClick={(e) => e.stopPropagation()}>
                    {isEmailProtected ? (
                      <Lock size={14} className="text-neutral-600" />
                    ) : (
                      <input
                        type="checkbox"
                        checked={selected}
                        onChange={() => onToggleSelect(email.id)}
                        className="w-3.5 h-3.5 rounded accent-primary-500"
                      />
                    )}
                  </div>

                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <p className="text-[13px] font-medium text-neutral-200 truncate flex-1">
                        {email.sender.split('<')[0].trim() || email.sender}
                      </p>
                      <span className="text-[11px] text-neutral-600 flex-shrink-0">
                        {formatTime(email.date)}
                      </span>
                    </div>
                    <p className="text-[12px] text-neutral-400 truncate">
                      {email.subject || '(No Subject)'}
                    </p>
                    <p className="text-[11px] text-neutral-600 truncate mt-0.5">
                      {email.snippet}
                    </p>
                  </div>

                  <span className={`px-2.5 py-1 rounded-md text-[11px] font-semibold border ${getCategoryColor(email.category)} flex-shrink-0`}>
                    {email.category}
                  </span>

                  <div className="flex items-center gap-2 flex-shrink-0">
                    <div className="w-16">
                      <div className="h-1 bg-white/[0.06] rounded-full overflow-hidden">
                        <div
                          className="h-full bg-gradient-to-r from-primary-500/70 to-primary-400/70 transition-all duration-500"
                          style={{ width: `${Math.round((email.confidence || 0) * 100)}%` }}
                        />
                      </div>
                    </div>
                  </div>
                </motion.div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};

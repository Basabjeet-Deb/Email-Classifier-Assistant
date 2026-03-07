import { useState } from 'react';
import { Lock, MoreVertical, Trash2, Archive, AlertCircle, Check } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import toast from 'react-hot-toast';
import { emailAPI } from '../api/client';

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

const getSuggestedAction = (category) => {
  const actions = {
    'Important': { action: 'Keep', color: 'text-emerald-400', icon: '✓' },
    'Transactional': { action: 'Keep', color: 'text-blue-400', icon: '✓' },
    'Promotional': { action: 'Archive', color: 'text-amber-400', icon: '📦' },
    'Social': { action: 'Archive', color: 'text-cyan-400', icon: '📦' },
    'Spam': { action: 'Delete', color: 'text-red-400', icon: '🗑️' },
  };
  return actions[category] || { action: 'Review', color: 'text-neutral-400', icon: '?' };
};

const getClassifierBadge = (classifier) => {
  if (!classifier) {
    return { color: 'text-neutral-400', bg: 'bg-neutral-500/10', label: '?' };
  }
  
  const classifierLower = classifier.toLowerCase();
  
  // Check for classifier type (case-insensitive)
  if (classifierLower.includes('zero-shot') || classifierLower.includes('zero shot')) {
    return { color: 'text-violet-400', bg: 'bg-violet-500/10', label: 'AI' };
  } else if (classifierLower.includes('tfidf') || classifierLower.includes('tf-idf')) {
    return { color: 'text-blue-400', bg: 'bg-blue-500/10', label: 'ML' };
  } else if (classifierLower.includes('keyword')) {
    return { color: 'text-emerald-400', bg: 'bg-emerald-500/10', label: 'Rule' };
  }
  
  return { color: 'text-neutral-400', bg: 'bg-neutral-500/10', label: '?' };
};

export const EmailTableEnhanced = ({ 
  emails, 
  selectedIds, 
  onToggleSelect, 
  onToggleSelectAll, 
  onDelete, 
  onArchive, 
  searchQuery,
  onFeedbackSubmit 
}) => {
  const [selectedEmail, setSelectedEmail] = useState(null);
  const [filterCategory, setFilterCategory] = useState('all');
  const [feedbackEmail, setFeedbackEmail] = useState(null);
  const [selectedCorrectCategory, setSelectedCorrectCategory] = useState('');
  const [submittingFeedback, setSubmittingFeedback] = useState(false);

  const allSelected = emails.length > 0 && selectedIds.length === emails.filter(e => !isProtected(e.category)).length;

  const filteredEmails = filterCategory === 'all'
    ? emails
    : emails.filter(e => e.category === filterCategory);

  const categories = ['all', ...new Set(emails.map(e => e.category))];
  const allCategories = ['Important', 'Transactional', 'Promotional', 'Social', 'Spam'];

  const handleFeedbackSubmit = async () => {
    if (!selectedCorrectCategory || !feedbackEmail) return;

    setSubmittingFeedback(true);
    try {
      await emailAPI.submitFeedback({
        email_id: feedbackEmail.id,
        sender: feedbackEmail.sender || 'unknown@email.com',
        subject: feedbackEmail.subject || '',
        body: feedbackEmail.snippet || '',
        predicted_category: feedbackEmail.category,
        correct_category: selectedCorrectCategory,
        confidence: feedbackEmail.confidence,
        classifier_used: feedbackEmail.classifier_used,
      });

      toast.success(
        <div className="flex flex-col gap-1">
          <span className="font-semibold">Thanks for your feedback!</span>
          <span className="text-sm text-neutral-400">This will help improve the classifier</span>
        </div>,
        { duration: 3000 }
      );

      setFeedbackEmail(null);
      setSelectedCorrectCategory('');
      
      if (onFeedbackSubmit) {
        onFeedbackSubmit(feedbackEmail.id, selectedCorrectCategory);
      }
    } catch (error) {
      console.error('Feedback submission error:', error);
      toast.error('Failed to submit feedback. Please try again.');
    } finally {
      setSubmittingFeedback(false);
    }
  };

  if (emails.length === 0) {
    return (
      <div className="ethereal-card glass rounded-xl p-16 text-center border border-violet-500/20 relative overflow-hidden">
        <div className="absolute inset-0 opacity-30">
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-64 h-64 bg-violet-500/20 rounded-full blur-3xl animate-pulse" />
        </div>
        
        <div className="relative z-10">
          <div className="w-20 h-20 mx-auto mb-6 bg-gradient-to-br from-violet-500/20 to-blue-500/20 rounded-2xl flex items-center justify-center border border-violet-500/30">
            <span className="text-5xl">📧</span>
          </div>
          <h3 className="text-xl font-bold text-neutral-100 mb-3">No emails to display</h3>
          <p className="text-neutral-400 text-sm max-w-md mx-auto leading-relaxed">
            {searchQuery
              ? `No emails match "${searchQuery}". Try a different search term.`
              : 'Click "Analyze Inbox" to start classifying your emails with AI-powered intelligence'
            }
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
      {/* Email List */}
      <div className="lg:col-span-2">
        <div className="glass rounded-xl overflow-hidden">
          {/* Filters */}
          <div className="p-4 border-b border-white/[0.04]">
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
                      ? 'bg-primary-500/15 text-primary-400'
                      : 'bg-white/[0.03] text-neutral-500 hover:bg-white/[0.06] hover:text-neutral-300'
                  }`}
                >
                  {cat === 'all' ? `All (${emails.length})` : `${cat} (${emails.filter(e => e.category === cat).length})`}
                </button>
              ))}
            </div>
          </div>

          {/* Table Header */}
          <div className="px-5 py-2.5 bg-white/[0.02] border-b border-white/[0.04] flex items-center gap-4 text-[10px] font-semibold text-neutral-500 uppercase tracking-wider">
            <input
              type="checkbox"
              checked={allSelected}
              onChange={onToggleSelectAll}
              className="w-3.5 h-3.5 rounded accent-primary-500"
            />
            <div className="flex-1">Email</div>
            <div className="w-32">Category</div>
            <div className="w-24">Confidence</div>
            <div className="w-16">Method</div>
            <div className="w-8"></div>
          </div>

          {/* Email List */}
          <div className="divide-y divide-white/[0.03] max-h-[550px] overflow-y-auto">
            {filteredEmails.map((email, index) => {
              const isEmailProtected = isProtected(email.category);
              const selected = selectedIds.includes(email.id);
              const confidence = Math.round((email.confidence || 0) * 100);
              const isActive = selectedEmail?.id === email.id;
              const classifierBadge = getClassifierBadge(email.classifier_used);

              return (
                <motion.div
                  key={email.id}
                  initial={{ opacity: 0, y: 15 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.025, duration: 0.3 }}
                  className={`px-5 py-3.5 flex items-center gap-4 cursor-pointer transition-all ${
                    isActive ? 'bg-primary-500/[0.06]' : 'hover:bg-white/[0.02]'
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
                    <p className="text-[13px] font-medium text-neutral-200 truncate">{email.subject || '(No Subject)'}</p>
                    <p className="text-[11px] text-neutral-500 truncate mt-0.5">{email.sender.split('<')[0]}</p>
                  </div>

                  <span className={`px-2.5 py-1 rounded-md text-[11px] font-semibold border ${getCategoryColor(email.category)}`}>
                    {email.category}
                  </span>

                  <div className="w-24">
                    <div className="flex items-center gap-2">
                      <div className="flex-1 h-1 bg-white/[0.06] rounded-full overflow-hidden">
                        <div
                          className="h-full bg-gradient-to-r from-primary-500/70 to-primary-400/70 transition-all duration-500"
                          style={{ width: `${confidence}%` }}
                        />
                      </div>
                      <span className="text-[11px] font-medium text-neutral-500">{confidence}%</span>
                    </div>
                  </div>

                  <div className="w-16">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${classifierBadge.bg} ${classifierBadge.color}`}>
                      {classifierBadge.label}
                    </span>
                  </div>

                  <button className="p-1 hover:bg-white/[0.05] rounded transition-all">
                    <MoreVertical size={14} className="text-neutral-600" />
                  </button>
                </motion.div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Email Preview with Feedback */}
      <div className="lg:col-span-1">
        <AnimatePresence mode="wait">
          {selectedEmail ? (
            <motion.div
              key={selectedEmail.id}
              initial={{ opacity: 0, x: 15 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 15 }}
              className="glass rounded-xl p-5 sticky top-0"
            >
              <div className="flex items-start justify-between mb-4">
                <h3 className="font-semibold text-neutral-200 text-sm">Email Details</h3>
                <button
                  onClick={() => setSelectedEmail(null)}
                  className="text-neutral-500 hover:text-neutral-300 transition-colors"
                >
                  ✕
                </button>
              </div>

              <div className="space-y-4">
                <div>
                  <p className="text-[10px] text-neutral-500 mb-1 uppercase tracking-wider">Subject</p>
                  <p className="text-[13px] font-medium text-neutral-200">{selectedEmail.subject || '(No Subject)'}</p>
                </div>

                <div>
                  <p className="text-[10px] text-neutral-500 mb-1 uppercase tracking-wider">From</p>
                  <p className="text-[12px] text-neutral-400">{selectedEmail.sender}</p>
                </div>

                <div>
                  <p className="text-[10px] text-neutral-500 mb-1 uppercase tracking-wider">Category</p>
                  <span className={`inline-block px-2.5 py-1 rounded-md text-[11px] font-semibold border ${getCategoryColor(selectedEmail.category)}`}>
                    {selectedEmail.category}
                  </span>
                </div>

                <div>
                  <p className="text-[10px] text-neutral-500 mb-1 uppercase tracking-wider">Confidence Score</p>
                  <div className="flex items-center gap-2">
                    <div className="flex-1 h-1.5 bg-white/[0.06] rounded-full overflow-hidden">
                      <div
                        className="h-full bg-gradient-to-r from-primary-500/70 to-primary-400/70"
                        style={{ width: `${Math.round((selectedEmail.confidence || 0) * 100)}%` }}
                      />
                    </div>
                    <span className="text-[12px] font-medium text-neutral-300">
                      {Math.round((selectedEmail.confidence || 0) * 100)}%
                    </span>
                  </div>
                </div>

                <div>
                  <p className="text-[10px] text-neutral-500 mb-1 uppercase tracking-wider">Classifier Used</p>
                  <p className="text-[12px] text-neutral-300">{selectedEmail.classifier_used || 'Unknown'}</p>
                </div>

                <div>
                  <p className="text-[10px] text-neutral-500 mb-1 uppercase tracking-wider">Suggested Action</p>
                  <div className="flex items-center gap-2">
                    <span className="text-base">{getSuggestedAction(selectedEmail.category).icon}</span>
                    <span className={`text-[12px] font-semibold ${getSuggestedAction(selectedEmail.category).color}`}>
                      {getSuggestedAction(selectedEmail.category).action}
                    </span>
                  </div>
                </div>

                <div>
                  <p className="text-[10px] text-neutral-500 mb-1.5 uppercase tracking-wider">Preview</p>
                  <p className="text-[12px] text-neutral-400 leading-relaxed">{selectedEmail.snippet}</p>
                </div>

                {/* Feedback Section */}
                {feedbackEmail?.id === selectedEmail.id ? (
                  <div className="pt-3 border-t border-white/[0.05]">
                    <div className="flex items-center gap-2 mb-3">
                      <AlertCircle size={14} className="text-amber-400" />
                      <p className="text-[11px] font-semibold text-neutral-300">Wrong Category?</p>
                    </div>
                    <select
                      value={selectedCorrectCategory}
                      onChange={(e) => setSelectedCorrectCategory(e.target.value)}
                      className="w-full px-3 py-2 bg-dark-800 border border-white/[0.06] rounded-lg text-[12px] text-neutral-300 focus:outline-none focus:ring-1 focus:ring-primary-500/30 mb-2"
                    >
                      <option value="">Select correct category</option>
                      {allCategories.filter(cat => cat !== selectedEmail.category).map(cat => (
                        <option key={cat} value={cat}>{cat}</option>
                      ))}
                    </select>
                    <div className="flex gap-2">
                      <button
                        onClick={handleFeedbackSubmit}
                        disabled={!selectedCorrectCategory || submittingFeedback}
                        className="flex-1 flex items-center justify-center gap-2 px-3 py-2 bg-primary-500/15 text-primary-400 rounded-lg hover:bg-primary-500/20 transition-all text-[12px] font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        {submittingFeedback ? (
                          <>
                            <div className="w-3 h-3 border-2 border-primary-400 border-t-transparent rounded-full animate-spin" />
                            <span>Submitting...</span>
                          </>
                        ) : (
                          <>
                            <Check size={14} />
                            <span>Submit</span>
                          </>
                        )}
                      </button>
                      <button
                        onClick={() => {
                          setFeedbackEmail(null);
                          setSelectedCorrectCategory('');
                        }}
                        className="px-3 py-2 bg-white/[0.04] text-neutral-400 rounded-lg hover:bg-white/[0.06] transition-all text-[12px] font-medium"
                      >
                        Cancel
                      </button>
                    </div>
                  </div>
                ) : (
                  <button
                    onClick={() => setFeedbackEmail(selectedEmail)}
                    className="w-full flex items-center justify-center gap-2 px-3 py-2 bg-amber-500/10 text-amber-400 rounded-lg hover:bg-amber-500/15 transition-all text-[12px] font-medium border border-amber-500/20"
                  >
                    <AlertCircle size={14} />
                    <span>Wrong Category?</span>
                  </button>
                )}

                {/* Actions */}
                {!isProtected(selectedEmail.category) && (
                  <div className="pt-3 border-t border-white/[0.05] flex gap-2">
                    <button
                      onClick={() => {
                        if (!selectedIds.includes(selectedEmail.id)) {
                          onToggleSelect(selectedEmail.id);
                        }
                        setTimeout(() => onDelete(), 100);
                      }}
                      className="flex-1 flex items-center justify-center gap-2 px-3 py-2 bg-red-500/10 text-red-400 rounded-lg hover:bg-red-500/15 transition-all text-[12px] font-medium"
                    >
                      <Trash2 size={14} />
                      <span>Delete</span>
                    </button>
                    <button
                      onClick={() => onArchive && onArchive(selectedEmail.id)}
                      className="flex-1 flex items-center justify-center gap-2 px-3 py-2 bg-white/[0.04] text-neutral-400 rounded-lg hover:bg-white/[0.06] transition-all text-[12px] font-medium"
                    >
                      <Archive size={14} />
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
              className="glass rounded-xl p-10 text-center"
            >
              <div className="text-3xl mb-3">👆</div>
              <p className="text-neutral-500 text-sm">Select an email to view details</p>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};

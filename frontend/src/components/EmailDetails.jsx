import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Trash2, Archive, AlertCircle, Check, ChevronDown, ChevronUp, Sparkles } from 'lucide-react';
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
    'Important': { action: 'Keep', color: 'text-emerald-400', icon: '✓', bg: 'bg-emerald-500/10' },
    'Transactional': { action: 'Keep', color: 'text-blue-400', icon: '✓', bg: 'bg-blue-500/10' },
    'Promotional': { action: 'Archive', color: 'text-amber-400', icon: '📦', bg: 'bg-amber-500/10' },
    'Social': { action: 'Archive', color: 'text-cyan-400', icon: '📦', bg: 'bg-cyan-500/10' },
    'Spam': { action: 'Delete', color: 'text-red-400', icon: '🗑️', bg: 'bg-red-500/10' },
  };
  return actions[category] || { action: 'Review', color: 'text-neutral-400', icon: '?', bg: 'bg-neutral-500/10' };
};

const getClassifierBadge = (classifier) => {
  if (!classifier) {
    return { color: 'text-neutral-400', bg: 'bg-neutral-500/10', label: 'Unknown', desc: 'Unknown method' };
  }
  
  const classifierLower = classifier.toLowerCase();
  
  // Check for classifier type (case-insensitive)
  if (classifierLower.includes('zero-shot') || classifierLower.includes('zero shot')) {
    return { color: 'text-violet-400', bg: 'bg-violet-500/10', label: 'AI Model', desc: 'Transformer-based zero-shot' };
  } else if (classifierLower.includes('tfidf') || classifierLower.includes('tf-idf')) {
    return { color: 'text-blue-400', bg: 'bg-blue-500/10', label: 'ML Model', desc: 'Structured TF-IDF + Logistic Regression' };
  } else if (classifierLower.includes('keyword')) {
    return { color: 'text-emerald-400', bg: 'bg-emerald-500/10', label: 'Rule-Based', desc: 'Keyword matching rules' };
  }
  
  return { color: 'text-neutral-400', bg: 'bg-neutral-500/10', label: 'Unknown', desc: 'Unknown method' };
};

export const EmailDetails = ({ 
  selectedEmail, 
  setSelectedEmail, 
  onToggleSelect, 
  selectedIds, 
  onDelete, 
  onArchive 
}) => {
  const [feedbackEmail, setFeedbackEmail] = useState(null);
  const [selectedCorrectCategory, setSelectedCorrectCategory] = useState('');
  const [submittingFeedback, setSubmittingFeedback] = useState(false);
  const [showAIExplanation, setShowAIExplanation] = useState(false);

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
    } catch (error) {
      console.error('Feedback submission error:', error);
      toast.error('Failed to submit feedback. Please try again.');
    } finally {
      setSubmittingFeedback(false);
    }
  };

  if (!selectedEmail) {
    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="glass rounded-xl p-16 text-center border border-white/[0.06]"
      >
        <div className="text-5xl mb-4">👆</div>
        <p className="text-neutral-500 text-sm">Select an email to view details</p>
      </motion.div>
    );
  }

  const confidence = Math.round((selectedEmail.confidence || 0) * 100);
  const classifierBadge = getClassifierBadge(selectedEmail.classifier_used);
  const suggestedAction = getSuggestedAction(selectedEmail.category);

  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={selectedEmail.id}
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        exit={{ opacity: 0, x: 20 }}
        className="glass rounded-xl overflow-hidden border border-white/[0.06]"
      >
        {/* Header */}
        <div className="p-5 border-b border-white/[0.04] bg-dark-800/30">
          <div className="flex items-start justify-between mb-3">
            <h3 className="font-semibold text-neutral-200 text-[15px]">Email Details</h3>
            <button
              onClick={() => setSelectedEmail(null)}
              className="text-neutral-500 hover:text-neutral-300 transition-colors p-1 hover:bg-white/[0.05] rounded"
            >
              ✕
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="p-5 space-y-5 max-h-[calc(100vh-280px)] overflow-y-auto">
          {/* Email Info */}
          <div className="space-y-4">
            <div>
              <p className="text-[10px] text-neutral-500 mb-1.5 uppercase tracking-wider font-semibold">Subject</p>
              <p className="text-[13px] font-medium text-neutral-200 leading-relaxed">
                {selectedEmail.subject || '(No Subject)'}
              </p>
            </div>

            <div>
              <p className="text-[10px] text-neutral-500 mb-1.5 uppercase tracking-wider font-semibold">From</p>
              <p className="text-[12px] text-neutral-300">{selectedEmail.sender}</p>
            </div>

            <div>
              <p className="text-[10px] text-neutral-500 mb-1.5 uppercase tracking-wider font-semibold">Preview</p>
              <p className="text-[12px] text-neutral-400 leading-relaxed">{selectedEmail.snippet}</p>
            </div>
          </div>

          {/* AI Classification Card */}
          <div className="p-4 rounded-xl bg-gradient-to-br from-violet-500/5 to-blue-500/5 border border-violet-500/20">
            <div className="flex items-center gap-2 mb-4">
              <Sparkles size={16} className="text-violet-400" />
              <h4 className="text-[13px] font-semibold text-neutral-200">AI Classification</h4>
            </div>

            <div className="space-y-4">
              {/* Category */}
              <div>
                <p className="text-[10px] text-neutral-500 mb-2 uppercase tracking-wider font-semibold">Category</p>
                <span className={`inline-block px-3 py-1.5 rounded-lg text-[12px] font-semibold border ${getCategoryColor(selectedEmail.category)}`}>
                  {selectedEmail.category}
                </span>
              </div>

              {/* Confidence Bar */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <p className="text-[10px] text-neutral-500 uppercase tracking-wider font-semibold">Confidence</p>
                  <span className="text-[12px] font-bold text-neutral-300">{confidence}%</span>
                </div>
                <div className="progress-bar">
                  <div
                    className="progress-fill confidence-bar-fill"
                    style={{ width: `${confidence}%` }}
                  />
                </div>
              </div>

              {/* Suggested Action */}
              <div>
                <p className="text-[10px] text-neutral-500 mb-2 uppercase tracking-wider font-semibold">Suggested Action</p>
                <div className={`flex items-center gap-2 px-3 py-2 rounded-lg ${suggestedAction.bg}`}>
                  <span className="text-lg">{suggestedAction.icon}</span>
                  <span className={`text-[13px] font-semibold ${suggestedAction.color}`}>
                    {suggestedAction.action}
                  </span>
                </div>
              </div>

              {/* Classifier Used */}
              <div>
                <p className="text-[10px] text-neutral-500 mb-2 uppercase tracking-wider font-semibold">Classifier Used</p>
                <div className={`px-3 py-2 rounded-lg ${classifierBadge.bg} border border-white/[0.05]`}>
                  <p className={`text-[12px] font-semibold ${classifierBadge.color}`}>{classifierBadge.label}</p>
                  <p className="text-[11px] text-neutral-500 mt-0.5">{classifierBadge.desc}</p>
                </div>
              </div>
            </div>
          </div>

          {/* AI Explanation Panel */}
          <div className="border border-white/[0.06] rounded-xl overflow-hidden">
            <button
              onClick={() => setShowAIExplanation(!showAIExplanation)}
              className="w-full p-4 flex items-center justify-between hover:bg-white/[0.02] transition-all"
            >
              <div className="flex items-center gap-2">
                <Sparkles size={14} className="text-primary-400" />
                <span className="text-[12px] font-semibold text-neutral-300">Why this classification?</span>
              </div>
              {showAIExplanation ? (
                <ChevronUp size={16} className="text-neutral-500" />
              ) : (
                <ChevronDown size={16} className="text-neutral-500" />
              )}
            </button>

            {showAIExplanation && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: 'auto', opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                className="px-4 pb-4 border-t border-white/[0.04]"
              >
                <div className="pt-3 space-y-3 text-[12px]">
                  <div>
                    <p className="text-neutral-500 mb-1">Model:</p>
                    <p className="text-neutral-300">{classifierBadge.desc}</p>
                  </div>
                  <div>
                    <p className="text-neutral-500 mb-1">Confidence Score:</p>
                    <p className="text-neutral-300">{confidence}% certainty in classification</p>
                  </div>
                  <div>
                    <p className="text-neutral-500 mb-1">Processing Time:</p>
                    <p className="text-neutral-300">
                      {selectedEmail.classification_time_ms ? `${selectedEmail.classification_time_ms}ms` : 'N/A'}
                    </p>
                  </div>
                </div>
              </motion.div>
            )}
          </div>

          {/* Feedback Section */}
          {feedbackEmail?.id === selectedEmail.id ? (
            <div className="p-4 border border-amber-500/20 rounded-xl bg-amber-500/5">
              <div className="flex items-center gap-2 mb-3">
                <AlertCircle size={14} className="text-amber-400" />
                <p className="text-[12px] font-semibold text-neutral-300">Wrong Category?</p>
              </div>
              <select
                value={selectedCorrectCategory}
                onChange={(e) => setSelectedCorrectCategory(e.target.value)}
                className="w-full px-3 py-2 bg-dark-800 border border-white/[0.06] rounded-lg text-[12px] text-neutral-300 focus:outline-none focus:ring-1 focus:ring-primary-500/30 mb-3"
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
              className="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-amber-500/10 text-amber-400 rounded-xl hover:bg-amber-500/15 transition-all text-[12px] font-medium border border-amber-500/20"
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
                className="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 bg-red-500/10 text-red-400 rounded-xl hover:bg-red-500/15 transition-all text-[12px] font-medium border border-red-500/20"
              >
                <Trash2 size={14} />
                <span>Delete</span>
              </button>
              <button
                onClick={() => onArchive && onArchive(selectedEmail.id)}
                className="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 bg-white/[0.04] text-neutral-400 rounded-xl hover:bg-white/[0.06] transition-all text-[12px] font-medium border border-white/[0.06]"
              >
                <Archive size={14} />
                <span>Archive</span>
              </button>
            </div>
          )}
        </div>
      </motion.div>
    </AnimatePresence>
  );
};

import { useState, useEffect } from 'react';
import { Save, RefreshCw, Database, Zap, Shield, TrendingUp } from 'lucide-react';
import toast from 'react-hot-toast';
import { emailAPI } from '../api/client';

export const Settings = () => {
  const [retraining, setRetraining] = useState(false);
  const [metrics, setMetrics] = useState(null);
  const [feedbackStats, setFeedbackStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchMetrics();
    fetchFeedbackStats();
  }, []);

  const fetchMetrics = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/metrics');
      const data = await response.json();
      setMetrics(data.metrics);
    } catch (error) {
      console.error('Failed to fetch metrics:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchFeedbackStats = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/feedback/stats');
      const data = await response.json();
      setFeedbackStats(data.stats);
    } catch (error) {
      console.error('Failed to fetch feedback stats:', error);
    }
  };

  const handleRetrain = async () => {
    setRetraining(true);
    try {
      await emailAPI.retrainTfidf();
      toast.success('Model retrained successfully!');
      // Refresh metrics after retraining
      setTimeout(() => {
        fetchMetrics();
        fetchFeedbackStats();
      }, 1000);
    } catch (error) {
      toast.error('Failed to retrain model');
    } finally {
      setRetraining(false);
    }
  };

  const avgConfidence = metrics ? (metrics.average_confidence * 100).toFixed(1) : '...';
  const emailsProcessed = metrics?.emails_processed || 0;

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-2xl font-bold text-neutral-100">Settings</h1>
        <p className="text-neutral-500 mt-1 text-sm">Configure your email classifier</p>
      </div>

      {/* ML Model Settings */}
      <div className="glass rounded-xl p-5">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-9 h-9 bg-primary-500/15 rounded-lg flex items-center justify-center">
            <Zap className="text-primary-400" size={18} />
          </div>
          <div>
            <h3 className="font-semibold text-neutral-200 text-sm">ML Model</h3>
            <p className="text-[11px] text-neutral-500">TF-IDF + Logistic Regression</p>
          </div>
        </div>

        <div className="space-y-3">
          <div className="flex items-center justify-between p-3.5 bg-white/[0.02] rounded-lg border border-white/[0.04]">
            <div>
              <p className="text-[13px] font-medium text-neutral-200">Confidence Threshold</p>
              <p className="text-[11px] text-neutral-500 mt-0.5">
                Current: {loading ? 'Loading...' : `${avgConfidence}%`} (Avg from {emailsProcessed} emails)
              </p>
            </div>
            <span className={`px-2.5 py-1 rounded-md text-[11px] font-medium ${
              avgConfidence >= 75 
                ? 'bg-emerald-500/15 text-emerald-400' 
                : avgConfidence >= 60 
                ? 'bg-amber-500/15 text-amber-400'
                : 'bg-red-500/15 text-red-400'
            }`}>
              {avgConfidence >= 75 ? 'Excellent' : avgConfidence >= 60 ? 'Good' : 'Needs Training'}
            </span>
          </div>

          <div className="flex items-center justify-between p-3.5 bg-white/[0.02] rounded-lg border border-white/[0.04]">
            <div>
              <p className="text-[13px] font-medium text-neutral-200">Categories</p>
              <p className="text-[11px] text-neutral-500 mt-0.5">5 categories for better accuracy</p>
            </div>
            <span className="text-[12px] font-medium text-neutral-400">5</span>
          </div>

          <div className="flex items-center justify-between p-3.5 bg-amber-500/[0.04] rounded-lg border border-amber-500/10">
            <div>
              <p className="text-[13px] font-medium text-neutral-200">Rate Limiting</p>
              <p className="text-[11px] text-neutral-500 mt-0.5">200ms delay + sequential processing</p>
            </div>
            <span className="px-2.5 py-1 bg-amber-500/15 text-amber-400 rounded-md text-[11px] font-medium">
              Protected
            </span>
          </div>

          {/* Self-Learning Stats */}
          {feedbackStats && (
            <div className="flex items-center justify-between p-3.5 bg-blue-500/[0.04] rounded-lg border border-blue-500/10">
              <div>
                <p className="text-[13px] font-medium text-neutral-200">Self-Learning Progress</p>
                <p className="text-[11px] text-neutral-500 mt-0.5">
                  {feedbackStats.total_samples} feedback samples collected
                </p>
              </div>
              <span className="px-2.5 py-1 bg-blue-500/15 text-blue-400 rounded-md text-[11px] font-medium">
                {feedbackStats.samples_until_retrain} until auto-retrain
              </span>
            </div>
          )}

          <button
            onClick={handleRetrain}
            disabled={retraining}
            className="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-primary-600/80 text-white rounded-lg hover:bg-primary-600 transition-all disabled:opacity-50 text-[13px] font-medium"
          >
            <RefreshCw size={16} className={retraining ? 'animate-spin' : ''} />
            <span>{retraining ? 'Retraining...' : 'Retrain Model'}</span>
          </button>
        </div>
      </div>

      {/* Database Settings */}
      <div className="glass rounded-xl p-5">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-9 h-9 bg-blue-500/15 rounded-lg flex items-center justify-center">
            <Database className="text-blue-400" size={18} />
          </div>
          <div>
            <h3 className="font-semibold text-neutral-200 text-sm">Database</h3>
            <p className="text-[11px] text-neutral-500">Classification history storage</p>
          </div>
        </div>

        <div className="space-y-3">
          <div className="flex items-center justify-between p-3.5 bg-white/[0.02] rounded-lg border border-white/[0.04]">
            <div>
              <p className="text-[13px] font-medium text-neutral-200">Storage Type</p>
              <p className="text-[11px] text-neutral-500 mt-0.5">SQLite (Local)</p>
            </div>
            <span className="px-2.5 py-1 bg-blue-500/15 text-blue-400 rounded-md text-[11px] font-medium">
              Connected
            </span>
          </div>

          <div className="flex items-center justify-between p-3.5 bg-white/[0.02] rounded-lg border border-white/[0.04]">
            <div>
              <p className="text-[13px] font-medium text-neutral-200">Analytics Retention</p>
              <p className="text-[11px] text-neutral-500 mt-0.5">Unlimited history</p>
            </div>
            <span className="text-[12px] font-medium text-neutral-400">∞</span>
          </div>
        </div>
      </div>

      {/* Security Settings */}
      <div className="glass rounded-xl p-5">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-9 h-9 bg-emerald-500/15 rounded-lg flex items-center justify-center">
            <Shield className="text-emerald-400" size={18} />
          </div>
          <div>
            <h3 className="font-semibold text-neutral-200 text-sm">Security</h3>
            <p className="text-[11px] text-neutral-500">Protected categories and permissions</p>
          </div>
        </div>

        <div className="space-y-3">
          <div className="flex items-center justify-between p-3.5 bg-white/[0.02] rounded-lg border border-white/[0.04]">
            <div>
              <p className="text-[13px] font-medium text-neutral-200">Protected Categories</p>
              <p className="text-[11px] text-neutral-500 mt-0.5">Banking, Work, Shopping</p>
            </div>
            <span className="px-2.5 py-1 bg-emerald-500/15 text-emerald-400 rounded-md text-[11px] font-medium">
              Enabled
            </span>
          </div>

          <div className="flex items-center justify-between p-3.5 bg-white/[0.02] rounded-lg border border-white/[0.04]">
            <div>
              <p className="text-[13px] font-medium text-neutral-200">Gmail Permissions</p>
              <p className="text-[11px] text-neutral-500 mt-0.5">Read, Modify, Label</p>
            </div>
            <span className="px-2.5 py-1 bg-emerald-500/15 text-emerald-400 rounded-md text-[11px] font-medium">
              Granted
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

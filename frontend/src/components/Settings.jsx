import { useState } from 'react';
import { Save, RefreshCw, Database, Zap, Shield } from 'lucide-react';
import toast from 'react-hot-toast';
import { emailAPI } from '../api/client';

export const Settings = () => {
  const [retraining, setRetraining] = useState(false);

  const handleRetrain = async () => {
    setRetraining(true);
    try {
      await emailAPI.retrainTfidf();
      toast.success('Model retrained successfully!');
    } catch (error) {
      toast.error('Failed to retrain model');
    } finally {
      setRetraining(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-neutral-900">Settings</h1>
        <p className="text-neutral-500 mt-1">Manage your email classifier settings</p>
      </div>

      {/* ML Model Settings */}
      <div className="bg-white rounded-xl shadow-card border border-neutral-200 p-6">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
            <Zap className="text-primary-600" size={20} />
          </div>
          <div>
            <h3 className="font-semibold text-neutral-900">ML Model</h3>
            <p className="text-sm text-neutral-500">TF-IDF + Logistic Regression</p>
          </div>
        </div>

        <div className="space-y-4">
          <div className="flex items-center justify-between p-4 bg-neutral-50 rounded-lg">
            <div>
              <p className="font-medium text-neutral-900">Confidence Threshold</p>
              <p className="text-sm text-neutral-500">Current: 70% (High accuracy mode)</p>
            </div>
            <span className="px-3 py-1 bg-green-100 text-green-700 rounded-lg text-sm font-medium">
              Active
            </span>
          </div>

          <div className="flex items-center justify-between p-4 bg-neutral-50 rounded-lg">
            <div>
              <p className="font-medium text-neutral-900">Categories</p>
              <p className="text-sm text-neutral-500">5 categories for better accuracy</p>
            </div>
            <span className="text-sm font-medium text-neutral-600">5</span>
          </div>

          <div className="flex items-center justify-between p-4 bg-amber-50 rounded-lg border border-amber-200">
            <div>
              <p className="font-medium text-neutral-900">Rate Limiting</p>
              <p className="text-sm text-neutral-500">200ms delay + sequential processing</p>
            </div>
            <span className="px-3 py-1 bg-amber-100 text-amber-700 rounded-lg text-sm font-medium">
              Protected
            </span>
          </div>

          <button
            onClick={handleRetrain}
            disabled={retraining}
            className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-all disabled:opacity-50"
          >
            <RefreshCw size={20} className={retraining ? 'animate-spin' : ''} />
            <span>{retraining ? 'Retraining...' : 'Retrain Model'}</span>
          </button>
        </div>
      </div>

      {/* Database Settings */}
      <div className="bg-white rounded-xl shadow-card border border-neutral-200 p-6">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-10 h-10 bg-secondary-100 rounded-lg flex items-center justify-center">
            <Database className="text-secondary-600" size={20} />
          </div>
          <div>
            <h3 className="font-semibold text-neutral-900">Database</h3>
            <p className="text-sm text-neutral-500">Classification history storage</p>
          </div>
        </div>

        <div className="space-y-4">
          <div className="flex items-center justify-between p-4 bg-neutral-50 rounded-lg">
            <div>
              <p className="font-medium text-neutral-900">Storage Type</p>
              <p className="text-sm text-neutral-500">SQLite (Local)</p>
            </div>
            <span className="px-3 py-1 bg-blue-100 text-blue-700 rounded-lg text-sm font-medium">
              Connected
            </span>
          </div>

          <div className="flex items-center justify-between p-4 bg-neutral-50 rounded-lg">
            <div>
              <p className="font-medium text-neutral-900">Analytics Retention</p>
              <p className="text-sm text-neutral-500">Unlimited history</p>
            </div>
            <span className="text-sm font-medium text-neutral-600">∞</span>
          </div>
        </div>
      </div>

      {/* Security Settings */}
      <div className="bg-white rounded-xl shadow-card border border-neutral-200 p-6">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-10 h-10 bg-accent-100 rounded-lg flex items-center justify-center">
            <Shield className="text-accent-600" size={20} />
          </div>
          <div>
            <h3 className="font-semibold text-neutral-900">Security</h3>
            <p className="text-sm text-neutral-500">Protected categories and permissions</p>
          </div>
        </div>

        <div className="space-y-3">
          <div className="flex items-center justify-between p-4 bg-neutral-50 rounded-lg">
            <div>
              <p className="font-medium text-neutral-900">Protected Categories</p>
              <p className="text-sm text-neutral-500">Banking, Work, Shopping</p>
            </div>
            <span className="px-3 py-1 bg-green-100 text-green-700 rounded-lg text-sm font-medium">
              Enabled
            </span>
          </div>

          <div className="flex items-center justify-between p-4 bg-neutral-50 rounded-lg">
            <div>
              <p className="font-medium text-neutral-900">Gmail Permissions</p>
              <p className="text-sm text-neutral-500">Read, Modify, Label</p>
            </div>
            <span className="px-3 py-1 bg-green-100 text-green-700 rounded-lg text-sm font-medium">
              Granted
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

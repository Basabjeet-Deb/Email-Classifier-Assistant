import { useAnalytics } from '../hooks/useAnalytics';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line } from 'recharts';
import { TrendingUp, Mail, Target, Zap } from 'lucide-react';
import { StatCard } from './StatCard';

const COLORS = ['#10b981', '#3b82f6', '#7c3aed', '#ef4444', '#6366f1'];

export const Analytics = ({ activeAccount }) => {
  const { data, isLoading } = useAnalytics(activeAccount, 30);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="w-12 h-12 border-4 border-primary-200 border-t-primary-600 rounded-full animate-spin" />
      </div>
    );
  }

  if (!data || !data.analytics) {
    return (
      <div className="flex flex-col items-center justify-center h-96 text-gray-400">
        <div className="text-6xl mb-4">📊</div>
        <p className="text-lg">No analytics data available yet</p>
        <p className="text-sm">Scan some emails to generate insights</p>
      </div>
    );
  }

  const { analytics, insights } = data;

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div>
        <h2 className="text-3xl font-bold text-gray-900">Analytics Dashboard</h2>
        <p className="text-gray-500 mt-1">Last 30 days of email classification insights</p>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <StatCard
          icon="📧"
          label="Total Emails"
          value={analytics.total_emails.toLocaleString()}
          gradient="bg-gradient-to-br from-blue-100 to-blue-200"
        />
        <StatCard
          icon="🎯"
          label="Avg Confidence"
          value={`${analytics.average_confidence}%`}
          gradient="bg-gradient-to-br from-purple-100 to-purple-200"
        />
        <StatCard
          icon="⚡"
          label="Avg Speed"
          value={`${analytics.average_processing_time}ms`}
          gradient="bg-gradient-to-br from-green-100 to-green-200"
        />
        <StatCard
          icon="😊"
          label="Sentiment"
          value={analytics.sentiment_distribution.POSITIVE > analytics.sentiment_distribution.NEGATIVE ? 'Positive' : 'Neutral'}
          gradient="bg-gradient-to-br from-yellow-100 to-yellow-200"
        />
      </div>

      {/* Insights */}
      {insights && insights.length > 0 && (
        <div className="glass rounded-2xl p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">AI Insights</h3>
          <div className="space-y-3">
            {insights.map((insight, index) => (
              <div key={index} className="flex items-start gap-3 p-3 bg-gradient-to-r from-primary-50 to-purple-50 rounded-lg border-l-4 border-primary-500">
                <span className="text-xl">💡</span>
                <span className="text-sm text-gray-700">{insight}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Category Distribution */}
        <div className="glass rounded-2xl p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Category Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={analytics.category_distribution}
                dataKey="count"
                nameKey="category"
                cx="50%"
                cy="50%"
                outerRadius={100}
                label
              >
                {analytics.category_distribution.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Daily Trend */}
        <div className="glass rounded-2xl p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Daily Trend</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={analytics.daily_trend}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="date" tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip />
              <Line type="monotone" dataKey="count" stroke="#6366f1" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Hourly Pattern */}
        <div className="glass rounded-2xl p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Emails by Hour</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={analytics.emails_by_hour.map((count, hour) => ({ hour: `${hour}:00`, count }))}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="hour" tick={{ fontSize: 10 }} />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip />
              <Bar dataKey="count" fill="#06b6d4" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Weekly Pattern */}
        <div className="glass rounded-2xl p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Emails by Day</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'].map((day, i) => ({ 
              day, 
              count: analytics.emails_by_day[i] 
            }))}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="day" tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip />
              <Bar dataKey="count" fill="#8b5cf6" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

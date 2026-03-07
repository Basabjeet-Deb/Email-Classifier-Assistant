import { useAnalytics } from '../hooks/useAnalytics';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line } from 'recharts';
import { StatCard } from './StatCard';

// Brighter, more visible colors for dark theme
const COLORS = ['#f59e0b', '#3b82f6', '#a78bfa', '#ef4444', '#10b981'];

const darkTooltipStyle = {
  backgroundColor: '#1f1f27',
  border: '1px solid rgba(255,255,255,0.2)',
  borderRadius: '8px',
  color: '#e0ddd6',
  fontSize: '12px',
};

export const Analytics = ({ activeAccount }) => {
  const { data, isLoading } = useAnalytics(activeAccount, 30);

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center h-96 space-y-4">
        <div className="relative">
          <div className="w-14 h-14 border-3 border-primary-500/20 border-t-primary-500 rounded-full animate-spin" />
          <div className="absolute inset-0 flex items-center justify-center">
            <span className="text-xl">📊</span>
          </div>
        </div>
        <div className="text-center space-y-2">
          <p className="text-base font-semibold text-neutral-200">Analyzing Your Emails...</p>
          <p className="text-sm text-neutral-500">Processing classification data and generating insights</p>
          <div className="flex items-center justify-center gap-2 text-xs text-neutral-600 mt-4">
            <div className="w-1.5 h-1.5 bg-primary-500 rounded-full animate-pulse" />
            <span>Calculating metrics</span>
            <div className="w-1.5 h-1.5 bg-primary-500 rounded-full animate-pulse delay-100" />
            <span>Building charts</span>
            <div className="w-1.5 h-1.5 bg-primary-500 rounded-full animate-pulse delay-200" />
            <span>Generating insights</span>
          </div>
        </div>
      </div>
    );
  }

  if (!data || !data.analytics || !data.analytics.total_emails) {
    return (
      <div className="flex flex-col items-center justify-center h-96">
        <div className="text-5xl mb-4">📊</div>
        <p className="text-base text-neutral-400">No analytics data available yet</p>
        <p className="text-sm text-neutral-600 mt-1">Scan some emails to generate insights</p>
      </div>
    );
  }

  const { analytics, insights } = data;
  
  // Ensure all required fields exist with defaults
  const safeAnalytics = {
    total_emails: analytics.total_emails || 0,
    average_confidence: analytics.average_confidence || 0,
    average_processing_time: analytics.average_processing_time || 0,
    sentiment_distribution: analytics.sentiment_distribution || { POSITIVE: 0, NEGATIVE: 0, NEUTRAL: 0 },
    category_distribution: analytics.category_distribution || [],
    daily_trend: analytics.daily_trend || [],
    emails_by_hour: analytics.emails_by_hour || Array(24).fill(0),
    emails_by_day: analytics.emails_by_day || Array(7).fill(0)
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-neutral-100">Analytics Dashboard</h2>
        <p className="text-neutral-500 mt-1 text-sm">Last 30 days of email classification insights</p>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <StatCard
          icon="📧"
          label="Total Emails"
          value={safeAnalytics.total_emails.toLocaleString()}
          gradient="bg-gradient-to-br from-blue-500/10 to-blue-600/5"
        />
        <StatCard
          icon="🎯"
          label="Avg Confidence"
          value={`${safeAnalytics.average_confidence}%`}
          gradient="bg-gradient-to-br from-violet-500/10 to-violet-600/5"
        />
        <StatCard
          icon="⚡"
          label="Avg Speed"
          value={`${safeAnalytics.average_processing_time}ms`}
          gradient="bg-gradient-to-br from-emerald-500/10 to-emerald-600/5"
        />
        <StatCard
          icon="😊"
          label="Sentiment"
          value={safeAnalytics.sentiment_distribution.POSITIVE > safeAnalytics.sentiment_distribution.NEGATIVE ? 'Positive' : 'Neutral'}
          gradient="bg-gradient-to-br from-amber-500/10 to-amber-600/5"
        />
      </div>

      {/* Insights */}
      {insights && insights.length > 0 && (
        <div className="glass rounded-xl p-5">
          <h3 className="text-sm font-semibold text-neutral-200 mb-3">AI Insights</h3>
          <div className="space-y-2">
            {insights.map((insight, index) => (
              <div key={index} className="flex items-start gap-3 p-3 bg-primary-500/[0.04] rounded-lg border-l-2 border-primary-500/40">
                <span className="text-base">💡</span>
                <span className="text-[13px] text-neutral-300">{insight}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        {/* Category Distribution */}
        <div className="glass rounded-xl p-5">
          <h3 className="text-sm font-semibold text-neutral-200 mb-4">Category Distribution</h3>
          <ResponsiveContainer width="100%" height={280}>
            <PieChart>
              <Pie
                data={safeAnalytics.category_distribution}
                dataKey="count"
                nameKey="category"
                cx="50%"
                cy="50%"
                outerRadius={95}
                label
                stroke="rgba(0,0,0,0.3)"
                strokeWidth={2}
              >
                {safeAnalytics.category_distribution.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip contentStyle={darkTooltipStyle} />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Daily Trend */}
        <div className="glass rounded-xl p-5">
          <h3 className="text-sm font-semibold text-neutral-200 mb-4">Daily Trend</h3>
          <ResponsiveContainer width="100%" height={280}>
            <LineChart data={safeAnalytics.daily_trend}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
              <XAxis dataKey="date" tick={{ fontSize: 11, fill: '#9ca3af' }} />
              <YAxis tick={{ fontSize: 11, fill: '#9ca3af' }} />
              <Tooltip contentStyle={darkTooltipStyle} />
              <Line type="monotone" dataKey="count" stroke="#f59e0b" strokeWidth={3} dot={{ fill: '#f59e0b', r: 4 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Hourly Pattern */}
        <div className="glass rounded-xl p-5">
          <h3 className="text-sm font-semibold text-neutral-200 mb-4">Emails by Hour</h3>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={safeAnalytics.emails_by_hour.map((count, hour) => ({ hour: `${hour}:00`, count }))}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
              <XAxis dataKey="hour" tick={{ fontSize: 10, fill: '#9ca3af' }} />
              <YAxis tick={{ fontSize: 11, fill: '#9ca3af' }} />
              <Tooltip contentStyle={darkTooltipStyle} />
              <Bar dataKey="count" fill="#3b82f6" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Weekly Pattern */}
        <div className="glass rounded-xl p-5">
          <h3 className="text-sm font-semibold text-neutral-200 mb-4">Emails by Day</h3>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'].map((day, i) => ({
              day,
              count: safeAnalytics.emails_by_day[i]
            }))}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
              <XAxis dataKey="day" tick={{ fontSize: 11, fill: '#9ca3af' }} />
              <YAxis tick={{ fontSize: 11, fill: '#9ca3af' }} />
              <Tooltip contentStyle={darkTooltipStyle} />
              <Bar dataKey="count" fill="#a78bfa" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

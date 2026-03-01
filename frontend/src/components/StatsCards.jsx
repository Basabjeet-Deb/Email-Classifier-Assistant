import { TrendingUp, TrendingDown, Mail, Target, Zap, CheckCircle } from 'lucide-react';

export const StatsCards = ({ totalScanned, avgConfidence, metrics }) => {
  const stats = [
    {
      title: 'Total Emails',
      value: totalScanned,
      icon: Mail,
      gradient: 'from-blue-500/10 to-blue-600/5',
      iconBg: 'bg-blue-500/15 text-blue-400',
      borderGlow: 'border-blue-500/30',
      trend: null,
    },
    {
      title: 'Avg Confidence',
      value: `${avgConfidence}%`,
      icon: Target,
      gradient: 'from-emerald-500/10 to-emerald-600/5',
      iconBg: 'bg-emerald-500/15 text-emerald-400',
      borderGlow: 'border-emerald-500/30',
      trend: avgConfidence > 80 ? 'up' : avgConfidence > 60 ? 'neutral' : 'down',
    },
    {
      title: 'Processing Speed',
      value: metrics?.avg_classification_time_ms
        ? `${Math.round(metrics.avg_classification_time_ms)}ms`
        : '0ms',
      icon: Zap,
      gradient: 'from-amber-500/10 to-amber-600/5',
      iconBg: 'bg-amber-500/15 text-amber-400',
      borderGlow: 'border-amber-500/30',
      trend: null,
    },
    {
      title: 'Classified',
      value: metrics?.category_distribution
        ? Object.values(metrics.category_distribution).reduce((a, b) => a + b, 0)
        : 0,
      icon: CheckCircle,
      gradient: 'from-violet-500/10 to-violet-600/5',
      iconBg: 'bg-violet-500/15 text-violet-400',
      borderGlow: 'border-violet-500/30',
      trend: 'up',
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      {stats.map((stat, index) => {
        const Icon = stat.icon;
        return (
          <div
            key={index}
            className={`ethereal-card glass rounded-xl p-5 bg-gradient-to-br ${stat.gradient} border ${stat.borderGlow} relative overflow-hidden group`}
          >
            {/* Glow effect on hover */}
            <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500">
              <div className={`absolute inset-0 bg-gradient-to-br ${stat.gradient} blur-xl`} />
            </div>
            
            <div className="relative z-10">
              <div className="flex items-start justify-between mb-3">
                <div className={`w-10 h-10 rounded-lg ${stat.iconBg} flex items-center justify-center shadow-lg`}>
                  <Icon size={20} />
                </div>
                {stat.trend && (
                  <div className={`flex items-center gap-1 text-xs font-medium ${stat.trend === 'up' ? 'text-emerald-400' : stat.trend === 'down' ? 'text-red-400' : 'text-neutral-500'
                    }`}>
                    {stat.trend === 'up' ? <TrendingUp size={14} /> : stat.trend === 'down' ? <TrendingDown size={14} /> : null}
                  </div>
                )}
              </div>
              <div>
                <p className="text-2xl font-bold text-neutral-100 mb-1">{stat.value}</p>
                <p className="text-xs text-neutral-500">{stat.title}</p>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
};

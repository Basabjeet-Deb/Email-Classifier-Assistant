import { TrendingUp, TrendingDown, Mail, Target, Zap, CheckCircle } from 'lucide-react';

export const StatsCards = ({ totalScanned, avgConfidence, metrics }) => {
  const stats = [
    {
      title: 'Total Emails',
      value: totalScanned,
      icon: Mail,
      color: 'blue',
      trend: null,
    },
    {
      title: 'Avg Confidence',
      value: `${avgConfidence}%`,
      icon: Target,
      color: 'green',
      trend: avgConfidence > 80 ? 'up' : avgConfidence > 60 ? 'neutral' : 'down',
    },
    {
      title: 'Processing Speed',
      value: metrics?.avg_classification_time_ms 
        ? `${Math.round(metrics.avg_classification_time_ms)}ms`
        : '0ms',
      icon: Zap,
      color: 'orange',
      trend: null,
    },
    {
      title: 'Classified',
      value: metrics?.category_distribution 
        ? Object.values(metrics.category_distribution).reduce((a, b) => a + b, 0)
        : 0,
      icon: CheckCircle,
      color: 'teal',
      trend: 'up',
    },
  ];

  const getColorClasses = (color) => {
    const colors = {
      blue: 'bg-blue-50 text-blue-600',
      green: 'bg-green-50 text-green-600',
      orange: 'bg-orange-50 text-orange-600',
      teal: 'bg-teal-50 text-teal-600',
    };
    return colors[color] || colors.blue;
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      {stats.map((stat, index) => {
        const Icon = stat.icon;
        return (
          <div key={index} className="bg-white rounded-xl p-6 shadow-card border border-neutral-200 hover:shadow-soft transition-all">
            <div className="flex items-start justify-between mb-4">
              <div className={`w-12 h-12 rounded-lg ${getColorClasses(stat.color)} flex items-center justify-center`}>
                <Icon size={24} />
              </div>
              {stat.trend && (
                <div className={`flex items-center gap-1 text-sm font-medium ${
                  stat.trend === 'up' ? 'text-green-600' : stat.trend === 'down' ? 'text-red-600' : 'text-neutral-600'
                }`}>
                  {stat.trend === 'up' ? <TrendingUp size={16} /> : stat.trend === 'down' ? <TrendingDown size={16} /> : null}
                </div>
              )}
            </div>
            <div>
              <p className="text-2xl font-bold text-neutral-900 mb-1">{stat.value}</p>
              <p className="text-sm text-neutral-500">{stat.title}</p>
            </div>
          </div>
        );
      })}
    </div>
  );
};

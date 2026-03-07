import { Brain, Zap, Database, TrendingUp } from 'lucide-react';
import { CategoryDistributionChart } from './CategoryDistributionChart';
import { ClassifierBreakdown } from './ClassifierBreakdown';

export const AIInsightsDashboard = ({ emails, metrics }) => {
  // Calculate AI system statistics
  const totalProcessed = emails.length;
  const avgConfidence = metrics?.avg_confidence 
    ? (metrics.avg_confidence * 100).toFixed(1)
    : 0;
  
  // Count classifier usage
  const classifierCounts = emails.reduce((acc, email) => {
    const classifier = email.classifier_used || 'Unknown';
    acc[classifier] = (acc[classifier] || 0) + 1;
    return acc;
  }, {});

  const transformerCalls = classifierCounts['Zero-Shot'] || 0;
  const tfidfCalls = classifierCounts['TF-IDF'] || 0;
  const keywordCalls = classifierCounts['Keyword'] || 0;
  
  // Calculate cache hit rate (emails classified with high confidence quickly)
  const cacheHits = emails.filter(e => e.confidence > 0.9 && e.classification_time_ms < 100).length;
  const cacheHitRate = totalProcessed > 0 ? ((cacheHits / totalProcessed) * 100).toFixed(0) : 0;

  const aiStats = [
    {
      label: 'Emails Processed',
      value: totalProcessed,
      icon: Database,
      color: 'text-blue-400',
      bgColor: 'bg-blue-500/10',
      borderColor: 'border-blue-500/20',
    },
    {
      label: 'Avg Confidence',
      value: `${avgConfidence}%`,
      icon: TrendingUp,
      color: 'text-emerald-400',
      bgColor: 'bg-emerald-500/10',
      borderColor: 'border-emerald-500/20',
    },
    {
      label: 'Transformer Calls',
      value: transformerCalls,
      icon: Brain,
      color: 'text-violet-400',
      bgColor: 'bg-violet-500/10',
      borderColor: 'border-violet-500/20',
    },
    {
      label: 'Cache Hit Rate',
      value: `${cacheHitRate}%`,
      icon: Zap,
      color: 'text-amber-400',
      bgColor: 'bg-amber-500/10',
      borderColor: 'border-amber-500/20',
    },
  ];

  return (
    <div className="space-y-5">
      {/* AI System Header */}
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-violet-500/20 to-blue-500/20 flex items-center justify-center border border-violet-500/30">
          <Brain size={20} className="text-violet-400" />
        </div>
        <div>
          <h2 className="text-lg font-bold text-neutral-100">AI Insights Dashboard</h2>
          <p className="text-xs text-neutral-500">Classification transparency and system metrics</p>
        </div>
      </div>

      {/* AI System Statistics */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        {aiStats.map((stat, index) => {
          const Icon = stat.icon;
          return (
            <div
              key={index}
              className={`glass rounded-xl p-4 ${stat.bgColor} border ${stat.borderColor} relative overflow-hidden group`}
            >
              <div className="relative z-10">
                <div className="flex items-center justify-between mb-2">
                  <Icon size={16} className={stat.color} />
                </div>
                <p className="text-2xl font-bold text-neutral-100 mb-0.5">{stat.value}</p>
                <p className="text-[10px] text-neutral-500 uppercase tracking-wider">{stat.label}</p>
              </div>
            </div>
          );
        })}
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        {/* Category Distribution */}
        <CategoryDistributionChart emails={emails} metrics={metrics} />
        
        {/* Classifier Breakdown */}
        <ClassifierBreakdown 
          classifierCounts={classifierCounts}
          totalEmails={totalProcessed}
        />
      </div>
    </div>
  );
};

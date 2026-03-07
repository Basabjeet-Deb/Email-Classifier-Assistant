import { Cpu, Sparkles, Tag } from 'lucide-react';

const classifierInfo = {
  'Zero-Shot': {
    icon: Sparkles,
    color: 'text-violet-400',
    bgColor: 'bg-violet-500/10',
    borderColor: 'border-violet-500/20',
    description: 'HuggingFace Transformer',
  },
  'TF-IDF': {
    icon: Cpu,
    color: 'text-blue-400',
    bgColor: 'bg-blue-500/10',
    borderColor: 'border-blue-500/20',
    description: 'Logistic Regression',
  },
  'Keyword': {
    icon: Tag,
    color: 'text-emerald-400',
    bgColor: 'bg-emerald-500/10',
    borderColor: 'border-emerald-500/20',
    description: 'Rule-based Matching',
  },
};

export const ClassifierBreakdown = ({ classifierCounts, totalEmails }) => {
  const classifiers = Object.entries(classifierCounts).map(([name, count]) => ({
    name,
    count,
    percentage: totalEmails > 0 ? ((count / totalEmails) * 100).toFixed(1) : 0,
    ...classifierInfo[name] || {
      icon: Cpu,
      color: 'text-neutral-400',
      bgColor: 'bg-neutral-500/10',
      borderColor: 'border-neutral-500/20',
      description: 'Unknown',
    },
  }));

  return (
    <div className="glass rounded-xl p-6 border border-white/5">
      <div className="flex items-center gap-2 mb-4">
        <Cpu size={16} className="text-neutral-400" />
        <h3 className="text-sm font-semibold text-neutral-200">Classifier Breakdown</h3>
      </div>

      {totalEmails === 0 ? (
        <div className="text-center py-8">
          <p className="text-sm text-neutral-500">No data to display</p>
        </div>
      ) : (
        <div className="space-y-3">
          {classifiers.map((classifier, index) => {
            const Icon = classifier.icon;
            return (
              <div
                key={index}
                className={`${classifier.bgColor} border ${classifier.borderColor} rounded-lg p-4`}
              >
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <Icon size={16} className={classifier.color} />
                    <div>
                      <p className="text-sm font-semibold text-neutral-200">{classifier.name}</p>
                      <p className="text-[10px] text-neutral-500">{classifier.description}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-lg font-bold text-neutral-100">{classifier.count}</p>
                    <p className="text-[10px] text-neutral-500">{classifier.percentage}%</p>
                  </div>
                </div>
                
                {/* Progress bar */}
                <div className="h-1.5 bg-white/5 rounded-full overflow-hidden">
                  <div
                    className={`h-full ${classifier.bgColor} transition-all duration-500`}
                    style={{ width: `${classifier.percentage}%` }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Info note */}
      <div className="mt-4 p-3 bg-white/[0.02] rounded-lg border border-white/5">
        <p className="text-[10px] text-neutral-500 leading-relaxed">
          <span className="font-semibold text-neutral-400">Classification Pipeline:</span> Keyword rules → TF-IDF model → Zero-shot transformer (fallback)
        </p>
      </div>
    </div>
  );
};

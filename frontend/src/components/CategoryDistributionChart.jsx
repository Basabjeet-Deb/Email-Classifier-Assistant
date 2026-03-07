import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';
import { BarChart3 } from 'lucide-react';

const COLORS = {
  'Important': '#ef4444',
  'Transactional': '#3b82f6',
  'Promotional': '#f59e0b',
  'Social': '#06b6d4',
  'Spam': '#6b7280',
};

export const CategoryDistributionChart = ({ emails, metrics }) => {
  // Calculate category distribution
  const categoryData = emails.reduce((acc, email) => {
    const category = email.category || 'Unknown';
    acc[category] = (acc[category] || 0) + 1;
    return acc;
  }, {});

  const chartData = Object.entries(categoryData).map(([name, value]) => ({
    name,
    value,
    color: COLORS[name] || '#6b7280',
  }));

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0];
      const percentage = ((data.value / emails.length) * 100).toFixed(1);
      return (
        <div className="glass rounded-lg p-3 border border-white/10">
          <p className="text-xs font-semibold text-neutral-200 mb-1">{data.name}</p>
          <p className="text-sm font-bold text-neutral-100">{data.value} emails</p>
          <p className="text-xs text-neutral-400">{percentage}% of total</p>
        </div>
      );
    }
    return null;
  };

  const CustomLegend = ({ payload }) => {
    return (
      <div className="flex flex-wrap gap-2 justify-center mt-4">
        {payload.map((entry, index) => (
          <div key={index} className="flex items-center gap-1.5">
            <div
              className="w-2.5 h-2.5 rounded-full"
              style={{ backgroundColor: entry.color }}
            />
            <span className="text-[11px] text-neutral-400">{entry.value}</span>
          </div>
        ))}
      </div>
    );
  };

  if (emails.length === 0) {
    return (
      <div className="glass rounded-xl p-6 border border-white/5">
        <div className="flex items-center gap-2 mb-4">
          <BarChart3 size={16} className="text-neutral-400" />
          <h3 className="text-sm font-semibold text-neutral-200">Category Distribution</h3>
        </div>
        <div className="text-center py-8">
          <p className="text-sm text-neutral-500">No data to display</p>
        </div>
      </div>
    );
  }

  return (
    <div className="glass rounded-xl p-6 border border-white/5">
      <div className="flex items-center gap-2 mb-4">
        <BarChart3 size={16} className="text-neutral-400" />
        <h3 className="text-sm font-semibold text-neutral-200">Category Distribution</h3>
      </div>
      
      <ResponsiveContainer width="100%" height={250}>
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={({ name, percent }) => `${(percent * 100).toFixed(0)}%`}
            outerRadius={80}
            fill="#8884d8"
            dataKey="value"
          >
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Pie>
          <Tooltip content={<CustomTooltip />} />
          <Legend content={<CustomLegend />} />
        </PieChart>
      </ResponsiveContainer>

      {/* Category Breakdown */}
      <div className="mt-4 space-y-2">
        {chartData.map((cat, index) => {
          const percentage = ((cat.value / emails.length) * 100).toFixed(1);
          return (
            <div key={index} className="flex items-center justify-between text-xs">
              <div className="flex items-center gap-2">
                <div
                  className="w-2 h-2 rounded-full"
                  style={{ backgroundColor: cat.color }}
                />
                <span className="text-neutral-400">{cat.name}</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-neutral-500">{cat.value}</span>
                <span className="text-neutral-600">({percentage}%)</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

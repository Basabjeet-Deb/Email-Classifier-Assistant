export const StatCard = ({ icon, label, value, gradient }) => {
  return (
    <div className="glass rounded-2xl p-6 hover:shadow-lg transition-all duration-300 hover:-translate-y-1">
      <div className="flex items-center gap-4">
        <div className={`w-14 h-14 rounded-xl flex items-center justify-center text-2xl ${gradient}`}>
          {icon}
        </div>
        <div>
          <div className="text-3xl font-bold text-gray-900">{value}</div>
          <div className="text-sm text-gray-500 uppercase tracking-wide">{label}</div>
        </div>
      </div>
    </div>
  );
};

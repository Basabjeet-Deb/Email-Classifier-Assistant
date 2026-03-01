export const StatCard = ({ icon, label, value, gradient }) => (
  <div className={`glass rounded-xl p-5 hover-glow ${gradient}`}>
    <div className="text-2xl mb-2">{icon}</div>
    <p className="text-xl font-bold text-neutral-100">{value}</p>
    <p className="text-xs text-neutral-500 mt-1">{label}</p>
  </div>
);

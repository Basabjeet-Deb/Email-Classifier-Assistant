import { useState } from 'react';
import { Lock } from 'lucide-react';
import { motion } from 'framer-motion';

const getCategoryBadge = (category) => {
  const badges = {
    'Banking/Financial': 'bg-green-100 text-green-700 border-green-300',
    'Shopping/Orders': 'bg-blue-100 text-blue-700 border-blue-300',
    'Work/Career': 'bg-purple-100 text-purple-700 border-purple-300',
    'Promotional': 'bg-red-100 text-red-700 border-red-300',
    'Personal/Other': 'bg-indigo-100 text-indigo-700 border-indigo-300',
  };
  return badges[category] || 'bg-gray-100 text-gray-700 border-gray-300';
};

const isProtected = (category) => {
  return ['Banking/Financial', 'Work/Career', 'Shopping/Orders'].some(c => category.includes(c));
};

export const EmailTable = ({ emails, selectedIds, onToggleSelect, onToggleSelectAll }) => {
  const allSelected = emails.length > 0 && selectedIds.length === emails.filter(e => !isProtected(e.category)).length;

  if (emails.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-gray-400">
        <div className="text-6xl mb-4">📧</div>
        <p className="text-lg">Click "Analyze Inbox" to start ML classification</p>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead className="bg-gray-50 sticky top-0 z-10">
          <tr>
            <th className="px-6 py-3 text-left">
              <input
                type="checkbox"
                checked={allSelected}
                onChange={onToggleSelectAll}
                className="w-4 h-4 text-primary-600 rounded focus:ring-2 focus:ring-primary-500"
              />
            </th>
            <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
              Category
            </th>
            <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
              Confidence
            </th>
            <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
              Sender
            </th>
            <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
              Subject & Preview
            </th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-100">
          {emails.map((email, index) => {
            const isEmailProtected = isProtected(email.category);
            const selected = selectedIds.includes(email.id);
            const confidence = Math.round((email.confidence || 0) * 100);

            return (
              <motion.tr
                key={email.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.05 }}
                className="bg-white hover:bg-gray-50 transition-colors"
              >
                <td className="px-6 py-4">
                  {isEmailProtected ? (
                    <Lock size={16} className="text-gray-400" title="Protected" />
                  ) : (
                    <input
                      type="checkbox"
                      checked={selected}
                      onChange={() => onToggleSelect(email.id)}
                      className="w-4 h-4 text-primary-600 rounded focus:ring-2 focus:ring-primary-500"
                    />
                  )}
                </td>
                <td className="px-6 py-4">
                  <span className={`inline-flex items-center px-3 py-1 rounded-lg text-xs font-semibold border ${getCategoryBadge(email.category)}`}>
                    {email.category}
                  </span>
                </td>
                <td className="px-6 py-4">
                  <div className="flex items-center gap-2">
                    <div className="w-16 h-2 bg-gray-200 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-gradient-to-r from-primary-500 to-primary-600 transition-all duration-500"
                        style={{ width: `${confidence}%` }}
                      />
                    </div>
                    <span className="text-xs font-medium text-gray-600">{confidence}%</span>
                  </div>
                </td>
                <td className="px-6 py-4 text-sm text-gray-600">
                  {email.sender.split('<')[0].substring(0, 30)}
                </td>
                <td className="px-6 py-4">
                  <div className="font-medium text-gray-900 mb-1">
                    {email.subject || '(No Subject)'}
                  </div>
                  <div className="text-sm text-gray-500 line-clamp-1">
                    {email.snippet.substring(0, 100)}...
                  </div>
                </td>
              </motion.tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
};

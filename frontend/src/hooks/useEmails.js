import { useState } from 'react';
import { emailAPI } from '../api/client';
import toast from 'react-hot-toast';

export const useEmails = () => {
  const [emails, setEmails] = useState([]);
  const [loading, setLoading] = useState(false);
  const [metrics, setMetrics] = useState(null);

  const scanInbox = async (accountId, maxResults, query) => {
    setLoading(true);
    try {
      const response = await emailAPI.scanEmails({
        account_id: accountId,
        max_results: maxResults,
        query: query,
      });
      
      if (response.data.status === 'success') {
        setEmails(response.data.emails);
        setMetrics(response.data.metrics);
        toast.success(`Analyzed ${response.data.processed_count} emails`);
        return response.data;
      }
    } catch (error) {
      toast.error('Failed to scan emails: ' + error.message);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const deleteEmails = async (accountId, messageIds) => {
    try {
      const response = await emailAPI.deleteEmails({
        account_id: accountId,
        message_ids: messageIds,
      });
      
      if (response.data.status === 'success') {
        setEmails(prev => prev.filter(e => !messageIds.includes(e.id)));
        toast.success(`Deleted ${response.data.deleted_count} emails`);
        return response.data;
      }
    } catch (error) {
      toast.error('Failed to delete emails: ' + error.message);
      throw error;
    }
  };

  return {
    emails,
    loading,
    metrics,
    scanInbox,
    deleteEmails,
  };
};

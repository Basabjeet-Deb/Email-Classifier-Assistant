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
        return response.data;
      }
    } catch (error) {
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const deleteEmails = async (accountId, messageIds, toastId) => {
    // Optimistic update - remove emails from UI immediately
    const previousEmails = [...emails];
    setEmails(prev => prev.filter(e => !messageIds.includes(e.id)));
    
    try {
      const response = await emailAPI.deleteEmails({
        account_id: accountId,
        message_ids: messageIds,
      });
      
      if (response.data.status === 'success') {
        // Success - emails already removed from UI
        return response.data;
      }
    } catch (error) {
      // Rollback on error - restore emails to UI
      setEmails(previousEmails);
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

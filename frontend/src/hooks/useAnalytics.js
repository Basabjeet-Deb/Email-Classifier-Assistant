import { useQuery } from '@tanstack/react-query';
import { emailAPI } from '../api/client';

export const useAnalytics = (accountId, days = 30) => {
  return useQuery({
    queryKey: ['analytics', accountId, days],
    queryFn: async () => {
      const response = await emailAPI.getAnalytics(accountId, days);
      return response.data;
    },
    enabled: !!accountId,
    staleTime: 60000, // 1 minute
  });
};

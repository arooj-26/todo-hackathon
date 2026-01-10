/**
 * Application providers for TanStack Query and other global state.
 *
 * This component wraps the application with necessary providers:
 * - QueryClientProvider for TanStack Query (server state management)
 */

'use client';

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { useState } from 'react';

/**
 * Props for Providers component.
 */
interface ProvidersProps {
  children: React.ReactNode;
}

/**
 * Default configuration for TanStack Query.
 */
const defaultQueryConfig = {
  queries: {
    // Cache time: how long data stays in cache after becoming inactive
    gcTime: 1000 * 60 * 5, // 5 minutes

    // Stale time: how long data is considered fresh
    staleTime: 1000 * 60, // 1 minute

    // Retry failed requests
    retry: 2,

    // Refetch on window focus (useful for real-time updates)
    refetchOnWindowFocus: true,

    // Refetch on reconnect
    refetchOnReconnect: true,

    // Refetch on mount if data is stale
    refetchOnMount: true,
  },
  mutations: {
    // Retry failed mutations
    retry: 1,
  },
};

/**
 * Application providers component.
 *
 * Wraps the application with TanStack Query provider and other
 * global state providers. Uses client-side state to ensure
 * QueryClient is not shared between requests in SSR.
 *
 * @param props - Component props
 * @returns Provider-wrapped children
 */
export function Providers({ children }: ProvidersProps) {
  // Create QueryClient instance using useState to ensure it's only
  // created once per client-side session (important for SSR)
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: defaultQueryConfig,
      })
  );

  return (
    <QueryClientProvider client={queryClient}>
      {children}
      {/* Show React Query DevTools in development */}
      {process.env.NODE_ENV === 'development' && (
        <ReactQueryDevtools initialIsOpen={false} />
      )}
    </QueryClientProvider>
  );
}

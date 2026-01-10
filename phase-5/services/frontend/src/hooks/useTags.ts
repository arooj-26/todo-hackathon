/**
 * Custom hook for tag management with TanStack Query.
 *
 * Provides queries and mutations for:
 * - Listing tags with autocomplete search
 * - Creating new tags
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { api } from '../lib/api';

/**
 * Tag interface.
 */
export interface Tag {
  id: number;
  name: string;
  usage_count: number;
}

/**
 * Tag creation data.
 */
export interface TagCreate {
  name: string;
}

/**
 * Tag list response.
 */
export interface TagListResponse {
  tags: Tag[];
}

/**
 * Tag list query parameters.
 */
export interface TagListParams {
  search?: string;
  limit?: number;
}

/**
 * Hook for tag management operations.
 *
 * @param params - Optional query parameters for tag list
 * @returns Tag queries and mutations
 */
export function useTags(params?: TagListParams) {
  const queryClient = useQueryClient();

  // Query for tag list with autocomplete
  const tagsQuery = useQuery<TagListResponse>({
    queryKey: ['tags', params],
    queryFn: async () => {
      const queryParams = new URLSearchParams();
      if (params?.search) queryParams.set('search', params.search);
      if (params?.limit) queryParams.set('limit', params.limit.toString());

      const endpoint = `/tags${queryParams.toString() ? `?${queryParams}` : ''}`;
      return api.get<TagListResponse>(endpoint);
    },
  });

  // Mutation for creating a tag
  const createTagMutation = useMutation({
    mutationFn: async (tagData: TagCreate) => {
      return api.post<Tag>('/tags', tagData);
    },
    onSuccess: () => {
      // Invalidate and refetch tags list
      queryClient.invalidateQueries({ queryKey: ['tags'] });
    },
  });

  return {
    // Queries
    tags: tagsQuery.data?.tags ?? [],
    isLoading: tagsQuery.isLoading,
    isError: tagsQuery.isError,
    error: tagsQuery.error,

    // Mutations
    createTag: createTagMutation.mutate,
    createTagAsync: createTagMutation.mutateAsync,
    isCreating: createTagMutation.isPending,

    // Refetch
    refetch: tagsQuery.refetch,
  };
}

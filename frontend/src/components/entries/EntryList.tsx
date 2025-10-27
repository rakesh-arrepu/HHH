import React from 'react';
import { gql, useQuery } from '@apollo/client';
import LoadingSpinner from '../common/LoadingSpinner';

type Entry = {
  id: string;
  section_type: 'Health' | 'Happiness' | 'Hela';
  content: string;
  entry_date: string;
};

interface EntryListProps {
  groupId?: string;
  limit?: number;
  emptyMessage?: string;
}

const MY_ENTRIES = gql`
  query MyEntries($groupId: String, $limit: Int, $offset: Int) {
    myEntries(groupId: $groupId, limit: $limit, offset: 0) {
      id
      section_type
      content
      entry_date
    }
  }
`;

export default function EntryList({ groupId, limit = 10, emptyMessage = 'No entries yet for the selected period.' }: EntryListProps) {
  const { data, loading, error } = useQuery(MY_ENTRIES, {
    variables: { groupId, limit, offset: 0 },
    fetchPolicy: 'cache-first',
  });

  if (loading) return <LoadingSpinner />;
  if (error) return <div className="text-red-600">Error loading entries: {error.message}</div>;

  const entries: Entry[] = data?.myEntries ?? [];
  if (entries.length === 0) {
    return <div className="text-gray-500">{emptyMessage}</div>;
  }

  return (
    <ul className="divide-y divide-gray-200">
      {entries.map((e) => (
        <li key={e.id} className="py-3">
          <div className="flex items-start justify-between">
            <div>
              <div className="flex items-center gap-2">
                <span className="inline-flex items-center rounded bg-blue-50 px-2 py-0.5 text-xs font-medium text-blue-700">
                  {e.section_type}
                </span>
                <span className="text-xs text-gray-500">
                  {new Date(e.entry_date).toLocaleDateString()}
                </span>
              </div>
              <p className="mt-1 text-gray-800">{e.content}</p>
            </div>
          </div>
        </li>
      ))}
    </ul>
  );
}

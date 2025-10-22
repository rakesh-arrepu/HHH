import React from 'react';
import { useQuery, gql } from '@apollo/client';
import LoadingSpinner from '../common/LoadingSpinner';

interface GroupListProps {
  onSelect: (groupId: string) => void;
}

const GET_MY_GROUPS = gql`
  query MyGroups {
    myGroups {
      id
      name
      description
      timezone
      created_at
    }
  }
`;

export default function GroupList({ onSelect }: GroupListProps) {
  const { loading, error, data } = useQuery(GET_MY_GROUPS);

  if (loading) return <LoadingSpinner />;
  if (error) return <div className="text-red-500">Error loading groups: {error.message}</div>;

  const groups = data?.myGroups || [];

  if (groups.length === 0) return <div className="text-gray-500">No groups found.</div>;

  return (
    <div className="space-y-4">
      {groups.map((group: any) => (
        <div key={group.id} className="p-4 border rounded-lg shadow-sm cursor-pointer" onClick={() => onSelect(group.id)}>
          <h3 className="text-lg font-semibold">{group.name}</h3>
          <p className="text-sm text-gray-600">{group.description}</p>
          <p className="text-xs text-gray-500">Timezone: {group.timezone}</p>
          <p className="text-xs text-gray-500">Created: {new Date(group.created_at).toLocaleDateString()}</p>
        </div>
      ))}
    </div>
  );
}

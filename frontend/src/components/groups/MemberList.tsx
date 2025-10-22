import React from 'react';
import { useQuery, gql } from '@apollo/client';
import LoadingSpinner from '../common/LoadingSpinner';
import UserCard from '../user/UserCard';

interface MemberListProps {
  groupId: string;
}

const GET_GROUP_MEMBERS = gql`
  query GetGroupMembers($id: String!) {
    group(id: $id) {
      members {
        id
        user {
          id
          name
          email
        }
        day_streak
        joined_at
      }
    }
  }
`;

export default function MemberList({ groupId }: MemberListProps) {
  const { loading, error, data } = useQuery(GET_GROUP_MEMBERS, { variables: { id: groupId } });

  if (loading) return <LoadingSpinner />;
  if (error) return <div className="text-red-500">Error loading members: {error.message}</div>;

  const members = data?.group?.members || [];

  if (members.length === 0) return <div className="text-gray-500">No members in this group.</div>;

  return (
    <div className="space-y-4">
      {members.map((member: any) => (
        <UserCard
          key={member.id}
          user={member.user}
          streak={member.day_streak}
          joinedAt={member.joined_at}
        />
      ))}
    </div>
  );
}

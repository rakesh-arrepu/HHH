import React from 'react';
import { useQuery, gql } from '@apollo/client';
import LoadingSpinner from '../components/common/LoadingSpinner';
import UserCard from '../components/user/UserCard';

const GET_PROFILE = gql`
  query Profile {
    me {
      id
      name
      email
    }
    streak
  }
`;

export default function Profile() {
  const { loading, error, data } = useQuery(GET_PROFILE);

  if (loading) return <LoadingSpinner />;
  if (error) return <div className="text-red-500">Error loading profile: {error.message}</div>;

  const user = data?.me;
  const streak = data?.streak;

  if (!user) return <div className="text-gray-500">No profile data.</div>;

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-6">My Profile</h1>
      <UserCard user={user} streak={streak} />
    </div>
  );
}

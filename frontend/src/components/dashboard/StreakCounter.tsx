import React from 'react';
import { gql, useQuery } from '@apollo/client';

const STREAK_QUERY = gql`
  query Streak($groupId: String) {
    streak(groupId: $groupId)
  }
`;

type Props = {
  groupId?: string;
};

export default function StreakCounter({ groupId }: Props) {
  const { data, loading, error } = useQuery(STREAK_QUERY, {
    variables: groupId ? { groupId } : undefined,
    fetchPolicy: 'cache-first',
  });

  const currentStreak: number = data?.streak ?? 0;

  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <h3 className="text-lg font-medium text-gray-900 mb-4">Streak Counter</h3>

      {loading && (
        <div className="text-center text-sm text-gray-600">Calculating your streak…</div>
      )}

      {error && (
        <div className="text-center text-sm text-red-600">
          Failed to load streak. Please try again later.
        </div>
      )}

      {!loading && !error && (
        <div className="text-center">
          <div className="text-6xl font-bold text-orange-500 mb-2">🔥</div>
          <div className="text-4xl font-bold text-orange-600 mb-1">
            {currentStreak}
          </div>
          <div className="text-sm text-gray-600 mb-4">days in a row</div>
          <div className="text-xs text-gray-500">
            Keep it up! Each daily entry extends your streak.
          </div>
        </div>
      )}
    </div>
  );
}

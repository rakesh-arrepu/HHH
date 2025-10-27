import React from 'react';
import { gql, useQuery } from '@apollo/client';

const DAILY_PROGRESS = gql`
  query DailyProgress($date: Date!, $groupId: String) {
    dailyProgress(date: $date, groupId: $groupId) {
      date
      totalEntries
      completedSections
      totalSections
      progressPercentage
    }
  }
`;

type Props = {
  groupId?: string;
  date?: string; // ISO date (YYYY-MM-DD). Defaults to today.
};

function todayISO() {
  return new Date().toISOString().slice(0, 10);
}

export default function ProgressBar({ groupId, date }: Props) {
  const variables = {
    date: date ?? todayISO(),
    ...(groupId ? { groupId } : {}),
  };

  const { data, loading, error } = useQuery(DAILY_PROGRESS, {
    variables,
    fetchPolicy: 'cache-first',
  });

  const progress = Math.round(data?.dailyProgress?.progressPercentage ?? 0);
  const totalSections = data?.dailyProgress?.totalSections ?? 0;
  const completedSections = data?.dailyProgress?.completedSections ?? 0;

  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <h3 className="text-lg font-medium text-gray-900 mb-4">Today's Progress</h3>

      {loading && (
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-gray-600">Completion</span>
            <span className="font-medium text-gray-500">Loading…</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-3 animate-pulse" />
          <div className="text-xs text-gray-500 text-center mt-2">Fetching progress…</div>
        </div>
      )}

      {error && (
        <div className="text-sm text-red-600">
          Failed to load progress. Please try again later.
        </div>
      )}

      {!loading && !error && (
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-gray-600">Completion</span>
            <span className="font-medium">
              {progress}% {totalSections > 0 ? `(${completedSections}/${totalSections})` : ''}
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-3">
            <div
              className="bg-green-500 h-3 rounded-full transition-all duration-300"
              style={{ width: `${Math.min(Math.max(progress, 0), 100)}%` }}
            />
          </div>
          <div className="text-xs text-gray-500 text-center mt-2">
            {progress >= 100 ? '🎉 All done for today!' : `${Math.max(100 - progress, 0)}% remaining`}
          </div>
        </div>
      )}
    </div>
  );
}

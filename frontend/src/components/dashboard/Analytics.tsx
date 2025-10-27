import React from 'react';
import { gql, useQuery } from '@apollo/client';

const GLOBAL_ANALYTICS = gql`
  query GlobalAnalytics {
    globalAnalytics {
      period { start end }
      totalUsers
      totalGroups
      totalEntries
      newUsers
      activeUsers
      activeGroups
      engagementRate
    }
  }
`;

const GROUP_ANALYTICS = gql`
  query GroupAnalytics($groupId: String!) {
    groupAnalytics(groupId: $groupId) {
      groupId
      period { start end }
      memberCount
      totalEntries
      activeUsers
      avgStreak
      dailyActivity { date entries }
    }
  }
`;

type Props = {
  groupId?: string;
};

export default function Analytics({ groupId }: Props) {
  const {
    data: globalData,
    loading: globalLoading,
    error: globalError,
  } = useQuery(GLOBAL_ANALYTICS, {
    // NOTE: On non-admin sessions this will error; we surface a friendly state.
    fetchPolicy: 'cache-first',
  });

  const {
    data: groupData,
    loading: groupLoading,
    error: groupError,
  } = useQuery(GROUP_ANALYTICS, {
    variables: groupId ? { groupId } : undefined,
    skip: !groupId,
    fetchPolicy: 'cache-first',
  });

  return (
    <div className="bg-white p-6 rounded-lg shadow space-y-6">
      <h3 className="text-lg font-medium text-gray-900">Analytics Overview</h3>

      {/* Global Analytics (Super Admin only) */}
      <section className="border border-gray-200 rounded-md p-4">
        <h4 className="text-sm font-semibold text-gray-700 mb-2">Global Analytics</h4>
        {globalLoading && <p className="text-gray-600 text-sm">Loading global analytics…</p>}
        {globalError && (
          <p className="text-orange-600 text-sm">
            Unable to load global analytics. You may need Super Admin access.
          </p>
        )}
        {!globalLoading && !globalError && globalData?.globalAnalytics ? (
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Total Users</span>
              <span className="text-sm font-semibold">
                {globalData.globalAnalytics.totalUsers}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Total Groups</span>
              <span className="text-sm font-semibold">
                {globalData.globalAnalytics.totalGroups}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Total Entries</span>
              <span className="text-sm font-semibold">
                {globalData.globalAnalytics.totalEntries}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Active Users</span>
              <span className="text-sm font-semibold">
                {globalData.globalAnalytics.activeUsers}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Engagement Rate</span>
              <span className="text-sm font-semibold">
                {(globalData.globalAnalytics.engagementRate ?? 0).toFixed(2)}%
              </span>
            </div>
          </div>
        ) : (
          !globalLoading &&
          !globalError && <p className="text-sm text-gray-500">No global analytics available.</p>
        )}
      </section>

      {/* Group Analytics */}
      <section className="border border-gray-200 rounded-md p-4">
        <h4 className="text-sm font-semibold text-gray-700 mb-2">Group Analytics</h4>
        {!groupId && (
          <p className="text-sm text-gray-500">
            Select a group to view analytics for that group.
          </p>
        )}
        {groupId && groupLoading && <p className="text-gray-600 text-sm">Loading group analytics…</p>}
        {groupId && groupError && (
          <p className="text-red-600 text-sm">Failed to load group analytics.</p>
        )}
        {groupId && !groupLoading && !groupError && groupData?.groupAnalytics ? (
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Group ID</span>
              <span className="text-sm font-semibold">{groupData.groupAnalytics.groupId}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Members</span>
              <span className="text-sm font-semibold">{groupData.groupAnalytics.memberCount}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Total Entries</span>
              <span className="text-sm font-semibold">{groupData.groupAnalytics.totalEntries}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Active Users</span>
              <span className="text-sm font-semibold">{groupData.groupAnalytics.activeUsers}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Avg Streak</span>
              <span className="text-sm font-semibold">
                {(groupData.groupAnalytics.avgStreak ?? 0).toFixed(1)} days
              </span>
            </div>
          </div>
        ) : (
          groupId &&
          !groupLoading &&
          !groupError && <p className="text-sm text-gray-500">No group analytics available.</p>
        )}
      </section>
    </div>
  );
}

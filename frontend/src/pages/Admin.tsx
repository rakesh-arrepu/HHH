import React, { useCallback, useEffect, useState } from 'react';
import { gql, useQuery } from '@apollo/client';
import Analytics from '../components/dashboard/Analytics';
import { API_URL } from '../lib/constants';
import { csrfHeaders } from '../lib/csrf';

const AUDIT_LOGS = gql`
  query AuditLogs($limit: Int, $offset: Int) {
    auditLogs(limit: $limit, offset: $offset) {
      id
      user_id
      action
      resource_type
      resource_id
      metadata
      ip_address
      created_at
    }
  }
`;

type BackupLog = {
  id: string;
  backup_file: string;
  backup_size: number;
  status: string;
  created_at: string;
};

type BackupStats = {
  total_backups: number;
  successful_backups: number;
  failed_backups: number;
  total_backup_size: number;
  latest_backup: null | {
    file: string | null;
    size: number | null;
    created_at: string | null;
  };
};

export default function Admin() {
  const [triggerLoading, setTriggerLoading] = useState(false);
  const [backupError, setBackupError] = useState<string | null>(null);
  const [backupMessage, setBackupMessage] = useState<string | null>(null);

  const [logs, setLogs] = useState<BackupLog[] | null>(null);
  const [logsLoading, setLogsLoading] = useState(false);
  const [stats, setStats] = useState<BackupStats | null>(null);
  const [statsLoading, setStatsLoading] = useState(false);

  const {
    data: auditData,
    loading: auditLoading,
    error: auditError,
    refetch: refetchAudit,
  } = useQuery(AUDIT_LOGS, {
    variables: { limit: 20, offset: 0 },
    fetchPolicy: 'cache-first',
  });

  const triggerBackup = useCallback(async () => {
    setTriggerLoading(true);
    setBackupError(null);
    setBackupMessage(null);
    try {
      const headers = await csrfHeaders();
      const res = await fetch(`${API_URL}/api/v1/backups/trigger`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
          ...headers,
        },
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok || data?.success === false) {
        const msg = (data && (data.message || data.detail)) || 'Backup failed';
        throw new Error(String(msg));
      }
      setBackupMessage(data.message || 'Backup triggered successfully');
      // Refresh logs/stats after a successful trigger
      await Promise.all([fetchLogs(), fetchStats(), refetchAudit()]);
    } catch (e) {
      setBackupError((e as Error).message);
    } finally {
      setTriggerLoading(false);
    }
  }, []);

  const fetchLogs = useCallback(async () => {
    setLogsLoading(true);
    setBackupError(null);
    try {
      const res = await fetch(`${API_URL}/api/v1/backups/logs`, {
        method: 'GET',
        credentials: 'include',
      });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        const msg = (data && (data.message || data.detail)) || 'Failed to load logs';
        throw new Error(String(msg));
      }
      const data: BackupLog[] = await res.json();
      setLogs(data);
    } catch (e) {
      setBackupError((e as Error).message);
    } finally {
      setLogsLoading(false);
    }
  }, []);

  const fetchStats = useCallback(async () => {
    setStatsLoading(true);
    setBackupError(null);
    try {
      const res = await fetch(`${API_URL}/api/v1/backups/stats`, {
        method: 'GET',
        credentials: 'include',
      });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        const msg = (data && (data.message || data.detail)) || 'Failed to load stats';
        throw new Error(String(msg));
      }
      const data: BackupStats = await res.json();
      setStats(data);
    } catch (e) {
      setBackupError((e as Error).message);
    } finally {
      setStatsLoading(false);
    }
  }, []);

  useEffect(() => {
    // Initial load of backup logs and stats
    fetchLogs();
    fetchStats();
  }, [fetchLogs, fetchStats]);

  return (
    <div className="container mx-auto px-4 py-6 space-y-8">
      <h1 className="text-2xl font-bold text-gray-900">Admin</h1>

      {/* Analytics - includes Global (Super Admin) and optional Group */}
      <section className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Analytics</h2>
        <Analytics />
      </section>

      {/* Backups section */}
      <section className="bg-white rounded-lg shadow p-6 space-y-4" aria-busy={triggerLoading || logsLoading || statsLoading}>
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-gray-900">Backups</h2>
          <div className="flex items-center gap-3">
            <button
              type="button"
              disabled={triggerLoading}
              onClick={triggerBackup}
              className="inline-flex items-center rounded-md bg-blue-600 px-4 py-2 text-white text-sm font-medium hover:bg-blue-700 disabled:opacity-50"
            >
              {triggerLoading ? 'Triggering…' : 'Trigger Backup'}
            </button>
            <button
              type="button"
              disabled={logsLoading || statsLoading}
              onClick={() => { fetchLogs(); fetchStats(); }}
              className="inline-flex items-center rounded-md bg-gray-200 px-4 py-2 text-gray-900 text-sm font-medium hover:bg-gray-300 disabled:opacity-50"
            >
              Refresh
            </button>
          </div>
        </div>

        {backupError && (
          <div role="alert" className="rounded-md border border-red-300 bg-red-50 px-4 py-3 text-sm text-red-800">
            {backupError}
          </div>
        )}
        {backupMessage && (
          <div role="status" aria-live="polite" className="rounded-md border border-green-300 bg-green-50 px-4 py-3 text-sm text-green-800">
            {backupMessage}
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Stats */}
          <div>
            <h3 className="text-sm font-semibold text-gray-700 mb-2">Stats</h3>
            {statsLoading && <p className="text-sm text-gray-600">Loading stats…</p>}
            {!statsLoading && stats ? (
              <div className="space-y-1 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Total Backups</span>
                  <span className="font-semibold">{stats.total_backups}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Successful</span>
                  <span className="font-semibold">{stats.successful_backups}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Failed</span>
                  <span className="font-semibold">{stats.failed_backups}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Total Size</span>
                  <span className="font-semibold">{(stats.total_backup_size / (1024 * 1024)).toFixed(2)} MB</span>
                </div>
                <div className="mt-2">
                  <span className="text-gray-600">Latest:</span>
                  {stats.latest_backup ? (
                    <div className="mt-1 text-xs text-gray-700">
                      <div>File: {stats.latest_backup.file}</div>
                      <div>Size: {stats.latest_backup.size} bytes</div>
                      <div>At: {stats.latest_backup.created_at}</div>
                    </div>
                  ) : (
                    <span className="ml-2 text-xs text-gray-500">No successful backups yet.</span>
                  )}
                </div>
              </div>
            ) : (
              !statsLoading && <p className="text-sm text-gray-500">No stats available.</p>
            )}
          </div>

          {/* Logs */}
          <div>
            <h3 className="text-sm font-semibold text-gray-700 mb-2">Recent Logs</h3>
            {logsLoading && <p className="text-sm text-gray-600">Loading logs…</p>}
            {!logsLoading && logs && logs.length > 0 ? (
              <div className="overflow-auto border rounded-md">
                <table className="min-w-full divide-y divide-gray-200 text-sm">
                  <caption className="sr-only">Backup logs</caption>
                  <thead className="bg-gray-50">
                    <tr>
                      <th scope="col" className="px-3 py-2 text-left font-medium text-gray-700">Time</th>
                      <th scope="col" className="px-3 py-2 text-left font-medium text-gray-700">File</th>
                      <th scope="col" className="px-3 py-2 text-left font-medium text-gray-700">Size</th>
                      <th scope="col" className="px-3 py-2 text-left font-medium text-gray-700">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {logs.map((l) => (
                      <tr key={l.id}>
                        <td className="px-3 py-2">{l.created_at}</td>
                        <td className="px-3 py-2 break-all">{l.backup_file}</td>
                        <td className="px-3 py-2">{(l.backup_size / (1024 * 1024)).toFixed(2)} MB</td>
                        <td className="px-3 py-2">{l.status}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              !logsLoading && <p className="text-sm text-gray-500">No logs available.</p>
            )}
          </div>
        </div>
      </section>

      {/* Audit Logs */}
      <section className="bg-white rounded-lg shadow p-6" aria-busy={auditLoading}>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900">Audit Logs</h2>
          <button
            type="button"
            disabled={auditLoading}
            onClick={() => refetchAudit()}
            className="inline-flex items-center rounded-md bg-gray-200 px-4 py-2 text-gray-900 text-sm font-medium hover:bg-gray-300 disabled:opacity-50"
          >
            {auditLoading ? 'Refreshing…' : 'Refresh'}
          </button>
        </div>
        {auditError && (
          <p className="text-sm text-red-600">
            Failed to load audit logs. You may need Super Admin access.
          </p>
        )}
        {!auditLoading && !auditError && auditData?.auditLogs?.length > 0 ? (
          <div className="overflow-auto border rounded-md">
            <table className="min-w-full divide-y divide-gray-200 text-sm">
              <caption className="sr-only">Audit logs</caption>
              <thead className="bg-gray-50">
                <tr>
                  <th scope="col" className="px-3 py-2 text-left font-medium text-gray-700">When</th>
                  <th scope="col" className="px-3 py-2 text-left font-medium text-gray-700">User</th>
                  <th scope="col" className="px-3 py-2 text-left font-medium text-gray-700">Action</th>
                  <th scope="col" className="px-3 py-2 text-left font-medium text-gray-700">Resource</th>
                  <th scope="col" className="px-3 py-2 text-left font-medium text-gray-700">IP</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {auditData.auditLogs.map((log: any) => (
                  <tr key={log.id}>
                    <td className="px-3 py-2">{log.created_at}</td>
                    <td className="px-3 py-2">{log.user_id}</td>
                    <td className="px-3 py-2">{log.action}</td>
                    <td className="px-3 py-2">{`${log.resource_type}:${log.resource_id}`}</td>
                    <td className="px-3 py-2">{log.ip_address || '-'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          !auditLoading &&
          !auditError && <p className="text-sm text-gray-500">No audit logs found.</p>
        )}
      </section>
    </div>
  );
}

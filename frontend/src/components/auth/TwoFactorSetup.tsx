import React, { useState } from 'react';
import { csrfHeaders } from '../../lib/csrf';
import { API_URL } from '../../lib/constants';

type Phase = 'idle' | 'provisioning' | 'verifying' | 'success';

export default function TwoFactorSetup() {
  const [phase, setPhase] = useState<Phase>('idle');
  const [error, setError] = useState<string | null>(null);
  const [provisioningUri, setProvisioningUri] = useState<string | null>(null);
  const [totpCode, setTotpCode] = useState<string>('');

  const beginSetup = async () => {
    setError(null);
    setPhase('provisioning');
    try {
      const headers = await csrfHeaders();
      const res = await fetch(`${API_URL}/api/v1/auth/2fa/enable`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
          ...headers,
        },
      });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        const msg = (data && data.detail) || 'Failed to start 2FA setup';
        throw new Error(String(msg));
      }
      const data = await res.json();
      setProvisioningUri(String(data.provisioning_uri));
    } catch (e) {
      setError((e as Error).message);
      setPhase('idle');
    }
  };

  const verify = async () => {
    setError(null);
    setPhase('verifying');
    try {
      const headers = await csrfHeaders();
      const res = await fetch(`${API_URL}/api/v1/auth/2fa/verify`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
          ...headers,
        },
        body: JSON.stringify({ totp_code: totpCode }),
      });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        const msg = (data && data.detail) || 'Invalid code';
        throw new Error(String(msg));
      }
      setPhase('success');
    } catch (e) {
      setError((e as Error).message);
      setPhase('provisioning');
    }
  };

  const isLoading = phase === 'provisioning' || phase === 'verifying';

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4">
      <div className="max-w-lg w-full space-y-6">
        <h1 className="text-2xl font-bold text-gray-900">Two-Factor Authentication (2FA)</h1>
        <p className="text-gray-600">
          2FA adds an extra layer of security. You will scan a QR code with an authenticator app (e.g., Google Authenticator, 1Password) and verify a 6-digit code.
        </p>

        {error && (
          <div role="alert" className="rounded-md border border-red-300 bg-red-50 px-4 py-3 text-sm text-red-800">
            {error}
          </div>
        )}

        {!provisioningUri && phase !== 'success' && (
          <button
            type="button"
            onClick={beginSetup}
            disabled={isLoading}
            className="inline-flex items-center justify-center rounded-md bg-blue-600 px-4 py-2 text-white text-sm font-medium hover:bg-blue-700 disabled:opacity-50"
          >
            {isLoading ? 'Starting…' : 'Begin 2FA Setup'}
          </button>
        )}

        {provisioningUri && phase !== 'success' && (
          <div className="space-y-4">
            <div>
              <h2 className="text-lg font-semibold text-gray-900 mb-2">Scan this QR in your authenticator app</h2>
              <div className="flex items-center justify-center p-4 bg-white border rounded-md">
                <img
                  src={`https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${encodeURIComponent(
                    provisioningUri
                  )}`}
                  alt="2FA QR code"
                />
              </div>
              <p className="mt-2 text-xs text-gray-500 break-all">
                If QR scanning fails, add this account manually using this URI:
                <br />
                <code className="text-gray-700">{provisioningUri}</code>
              </p>
            </div>

            <div>
              <label htmlFor="totpCode" className="block text-sm font-medium text-gray-700">
                Enter the 6-digit code from your app
              </label>
              <input
                id="totpCode"
                name="totpCode"
                inputMode="numeric"
                pattern="\d*"
                maxLength={6}
                className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-gray-900 focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                placeholder="123456"
                value={totpCode}
                onChange={(e) => setTotpCode(e.target.value)}
              />
            </div>

            <div className="flex items-center gap-3">
              <button
                type="button"
                onClick={verify}
                disabled={isLoading || totpCode.length < 6}
                className="inline-flex items-center justify-center rounded-md bg-green-600 px-4 py-2 text-white text-sm font-medium hover:bg-green-700 disabled:opacity-50"
              >
                {phase === 'verifying' ? 'Verifying…' : 'Verify & Enable 2FA'}
              </button>
              <button
                type="button"
                onClick={() => {
                  setProvisioningUri(null);
                  setTotpCode('');
                  setError(null);
                  setPhase('idle');
                }}
                disabled={isLoading}
                className="inline-flex items-center justify-center rounded-md bg-gray-200 px-4 py-2 text-gray-900 text-sm font-medium hover:bg-gray-300 disabled:opacity-50"
              >
                Reset
              </button>
            </div>
          </div>
        )}

        {phase === 'success' && (
          <div role="status" aria-live="polite" className="rounded-md border border-green-300 bg-green-50 px-4 py-3 text-sm text-green-800">
            Two-factor authentication is now enabled for your account.
          </div>
        )}
      </div>
    </div>
  );
}

import { API_URL } from './constants';

export const getCookie = (name: string): string | null => {
  const match = document.cookie.match(new RegExp(`(^|; )${name}=([^;]*)`));
  return match ? decodeURIComponent(match[2]) : null;
};

/**
 * Ensure CSRF cookie (hhh_csrf) exists by performing a safe GET if missing.
 * Returns the current CSRF token value (or null if unavailable).
 */
export const ensureCsrf = async (): Promise<string | null> => {
  let token = getCookie('hhh_csrf');
  if (!token) {
    // Hit a safe endpoint to trigger CSRF cookie issuance
    try {
      await fetch(`${API_URL}/api/v1/auth/health`, {
        method: 'GET',
        credentials: 'include',
      });
    } catch {
      // ignore network error here; caller can decide how to handle
    }
    token = getCookie('hhh_csrf');
  }
  return token;
};

/**
 * Returns headers including X-CSRF-Token if available.
 */
export const csrfHeaders = async (): Promise<HeadersInit> => {
  const token = await ensureCsrf();
  return token ? { 'X-CSRF-Token': token } : {};
};

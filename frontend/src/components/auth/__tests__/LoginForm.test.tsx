import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';

// Module mocks
jest.mock('../../../lib/constants', () => ({
  API_URL: 'http://test',
}));

// Mock CSRF helper to return a token header
jest.mock('../../../lib/csrf', () => ({
  csrfHeaders: async () => ({ 'X-CSRF-Token': 'test-token' }),
}));

// Mock navigate
const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => {
  const actual = jest.requireActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

import LoginForm from '../LoginForm';

describe('LoginForm', () => {
  beforeEach(() => {
    mockNavigate.mockReset();
    (globalThis as any).fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: async () => ({}),
    });
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  test('submits with CSRF header and navigates to dashboard on success', async () => {
    render(
      <MemoryRouter>
        <LoginForm />
      </MemoryRouter>
    );

    // Fill in credentials
    fireEvent.change(screen.getByLabelText(/email address/i), { target: { value: 'user@example.com' } });
    fireEvent.change(screen.getByLabelText(/password/i), { target: { value: 'secret123' } });

    // Submit
    fireEvent.submit(screen.getByRole('button', { name: /sign in/i }).closest('form') as HTMLFormElement);

    await waitFor(() => {
      // Assert fetch called with expected URL and headers
      expect(globalThis.fetch).toHaveBeenCalledTimes(1);
      const [url, init] = (globalThis.fetch as jest.Mock).mock.calls[0];
      expect(url).toBe('http://test/api/v1/auth/login');
      expect(init).toMatchObject({
        method: 'POST',
        credentials: 'include',
        headers: expect.objectContaining({
          'Content-Type': 'application/json',
          'X-CSRF-Token': 'test-token',
        }),
      });
      // Navigates on success
      expect(mockNavigate).toHaveBeenCalledWith('/dashboard');
    });
  });
});

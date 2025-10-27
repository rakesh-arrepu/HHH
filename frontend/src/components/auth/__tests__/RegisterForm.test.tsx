import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import RegisterForm from '../RegisterForm';

describe('RegisterForm', () => {
  test('shows inline error when passwords do not match and prevents submit', async () => {
    // Spy on fetch to ensure it is NOT called on mismatch
    const fetchSpy = jest.spyOn(globalThis as any, 'fetch');

    render(
      <MemoryRouter>
        <RegisterForm />
      </MemoryRouter>
    );

    // Fill fields
    fireEvent.change(screen.getByLabelText(/first name/i), { target: { value: 'John' } });
    fireEvent.change(screen.getByLabelText(/last name/i), { target: { value: 'Doe' } });
    fireEvent.change(screen.getByLabelText(/email address/i), { target: { value: 'john@example.com' } });
    fireEvent.change(screen.getByLabelText(/^password$/i), { target: { value: 'password123' } });
    fireEvent.change(screen.getByLabelText(/confirm password/i), { target: { value: 'passwordXYZ' } });

    // Submit
    fireEvent.submit(screen.getByRole('button', { name: /create account/i }).closest('form') as HTMLFormElement);

    // Error should be visible
    expect(await screen.findByRole('alert')).toHaveTextContent(/passwords do not match/i);

    // Ensure no network request was made
    expect(fetchSpy).not.toHaveBeenCalled();

    fetchSpy.mockRestore();
  });
});

import React from 'react';
import { render, screen } from '@testing-library/react';
import LoadingSpinner from '../LoadingSpinner';

describe('LoadingSpinner', () => {
  it('renders loading text', () => {
    render(<LoadingSpinner />);
    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });
});

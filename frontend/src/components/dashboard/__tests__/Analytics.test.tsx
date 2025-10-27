import React from 'react';
import { render, screen } from '@testing-library/react';

// Mock only useQuery from Apollo to control loading/error states
jest.mock('@apollo/client', () => {
  const actual = jest.requireActual('@apollo/client');
  return {
    ...actual,
    useQuery: jest.fn(),
  };
});

import { useQuery } from '@apollo/client';
import Analytics from '../Analytics';

describe('Analytics component', () => {
  test('renders friendly error for global analytics when access denied and shows group prompt when no groupId', () => {
    // First call is for GLOBAL_ANALYTICS -> return error
    (useQuery as jest.Mock).mockImplementationOnce(() => ({
      data: undefined,
      loading: false,
      error: new Error('Forbidden'),
    }));

    // Second call would be GROUP_ANALYTICS, but component uses skip: !groupId
    // Since no groupId is provided, it won't call useQuery for group analytics.
    render(<Analytics />);

    // Global analytics error message
    expect(
      screen.getByText(/Unable to load global analytics\. You may need Super Admin access\./i)
    ).toBeInTheDocument();

    // Group analytics prompt when no groupId
    expect(
      screen.getByText(/Select a group to view analytics for that group\./i)
    ).toBeInTheDocument();
  });
});

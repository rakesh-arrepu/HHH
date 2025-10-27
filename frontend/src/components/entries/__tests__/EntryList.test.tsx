import React from 'react';
import { render, screen } from '@testing-library/react';

// Mock only useQuery from Apollo to control loading/error/data states
jest.mock('@apollo/client', () => {
  const actual = jest.requireActual('@apollo/client');
  return {
    ...actual,
    useQuery: jest.fn(),
    gql: actual.gql,
  };
});

import { useQuery } from '@apollo/client';
import EntryList from '../EntryList';

describe('EntryList', () => {
  beforeEach(() => {
    jest.resetAllMocks();
  });

  test('renders loading state', () => {
    (useQuery as jest.Mock).mockReturnValue({
      loading: true,
      error: undefined,
      data: undefined,
    });

    render(<EntryList />);
    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });

  test('renders error state', () => {
    (useQuery as jest.Mock).mockReturnValue({
      loading: false,
      error: new Error('Boom'),
      data: undefined,
    });

    render(<EntryList />);
    expect(screen.getByText(/Error loading entries: Boom/i)).toBeInTheDocument();
  });

  test('renders empty state', () => {
    (useQuery as jest.Mock).mockReturnValue({
      loading: false,
      error: undefined,
      data: { myEntries: [] },
    });

    render(<EntryList emptyMessage="No entries for now." />);
    expect(screen.getByText(/No entries for now\./i)).toBeInTheDocument();
  });

  test('renders list items when data is present', () => {
    (useQuery as jest.Mock).mockReturnValue({
      loading: false,
      error: undefined,
      data: {
        myEntries: [
          {
            id: 'e1',
            section_type: 'Health',
            content: 'Walked 5k steps',
            entry_date: '2025-10-26',
          },
        ],
      },
    });

    render(<EntryList />);
    expect(screen.getByText(/Health/i)).toBeInTheDocument();
    expect(screen.getByText(/Walked 5k steps/i)).toBeInTheDocument();
  });
});

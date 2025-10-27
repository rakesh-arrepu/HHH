import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import Groups from '../Groups';

// Mock child components to isolate Groups page behavior
jest.mock('../../components/groups/GroupManagement', () => ({
  __esModule: true,
  default: () => <div data-testid="group-management">GroupManagement</div>,
}));

// This mock exposes a button to simulate selecting a group via onSelect
jest.mock('../../components/groups/GroupList', () => ({
  __esModule: true,
  default: ({ onSelect }: { onSelect: (id: string) => void }) => (
    <div>
      <div data-testid="group-list">GroupList</div>
      <button onClick={() => onSelect('group-123')} aria-label="select-group">
        Select Group
      </button>
    </div>
  ),
}));

jest.mock('../../components/groups/MemberList', () => ({
  __esModule: true,
  default: ({ groupId }: { groupId: string }) => (
    <div data-testid="member-list">Members for {groupId}</div>
  ),
}));

describe('Groups page', () => {
  test('renders sections and shows MemberList after selecting a group', () => {
    render(<Groups />);

    // Headings and sections render
    expect(screen.getByRole('heading', { level: 1, name: /Groups/i })).toBeInTheDocument();
    expect(screen.getByRole('heading', { level: 2, name: /Create New Group/i })).toBeInTheDocument();
    expect(screen.getByRole('heading', { level: 2, name: /My Groups/i })).toBeInTheDocument();
    expect(screen.getByTestId('group-management')).toBeInTheDocument();
    expect(screen.getByTestId('group-list')).toBeInTheDocument();

    // Initially, MemberList is not shown
    expect(screen.queryByTestId('member-list')).toBeNull();

    // Simulate selecting a group from GroupList
    fireEvent.click(screen.getByLabelText('select-group'));

    // MemberList should now appear with the selected group id
    expect(screen.getByTestId('member-list')).toHaveTextContent('Members for group-123');
  });
});

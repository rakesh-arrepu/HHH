import React, { useState } from 'react';
import GroupList from '../components/groups/GroupList';
import GroupManagement from '../components/groups/GroupManagement';
import MemberList from '../components/groups/MemberList';

export default function Groups() {
  const [selectedGroupId, setSelectedGroupId] = useState<string | null>(null);

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-6">Groups</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <h2 className="text-xl font-semibold mb-4">Create New Group</h2>
          <GroupManagement />
        </div>
        <div>
          <h2 className="text-xl font-semibold mb-4">My Groups</h2>
          <GroupList onSelect={setSelectedGroupId} />
        </div>
      </div>
      {selectedGroupId && (
        <div className="mt-8">
          <h2 className="text-xl font-semibold mb-4">Group Members</h2>
          <MemberList groupId={selectedGroupId} />
        </div>
      )}
    </div>
  );
}

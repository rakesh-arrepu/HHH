import React, { useState } from 'react';
import { useMutation, gql } from '@apollo/client';

const CREATE_GROUP = gql`
  mutation CreateGroup($name: String!, $description: String, $timezone: String) {
    createGroup(name: $name, description: $description, timezone: $timezone) {
      id
      name
      description
      timezone
    }
  }
`;

export default function GroupManagement() {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [timezone, setTimezone] = useState('UTC');
  const [createGroup, { loading, error }] = useMutation(CREATE_GROUP);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await createGroup({ variables: { name, description, timezone } });
      // Reset form or show success
      setName('');
      setDescription('');
      setTimezone('UTC');
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label htmlFor="name" className="block text-sm font-medium text-gray-700">Group Name</label>
        <input
          type="text"
          id="name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50"
          required
        />
      </div>
      <div>
        <label htmlFor="description" className="block text-sm font-medium text-gray-700">Description</label>
        <textarea
          id="description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50"
        />
      </div>
      <div>
        <label htmlFor="timezone" className="block text-sm font-medium text-gray-700">Timezone</label>
        <input
          type="text"
          id="timezone"
          value={timezone}
          onChange={(e) => setTimezone(e.target.value)}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50"
        />
      </div>
      <button
        type="submit"
        disabled={loading}
        className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:bg-gray-400"
      >
        {loading ? 'Creating...' : 'Create Group'}
      </button>
      {error && <div className="text-red-500">Error: {error.message}</div>}
    </form>
  );
}

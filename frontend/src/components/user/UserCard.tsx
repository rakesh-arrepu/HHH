import React from 'react';

interface User {
  id: string;
  name: string;
  email: string;
}

interface UserCardProps {
  user: User;
  streak?: number;
  joinedAt?: string;
}

export default function UserCard({ user, streak, joinedAt }: UserCardProps) {
  return (
    <div className="p-4 border rounded-lg shadow-sm">
      <h3 className="text-lg font-semibold">{user.name}</h3>
      <p className="text-sm text-gray-600">Email: {user.email}</p>
      {streak !== undefined && <p className="text-xs text-gray-500">Streak: {streak} days</p>}
      {joinedAt && <p className="text-xs text-gray-500">Joined: {new Date(joinedAt).toLocaleDateString()}</p>}
    </div>
  );
}

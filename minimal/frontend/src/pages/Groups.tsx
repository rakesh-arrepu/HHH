import { useState, useEffect } from 'react'
import { api } from '../api'

type Group = { id: number; name: string; owner_id: number; is_owner: boolean }
type Member = { id: number; user_id: number; name: string; email: string }

export default function Groups() {
  const [groups, setGroups] = useState<Group[]>([])
  const [selectedGroup, setSelectedGroup] = useState<Group | null>(null)
  const [members, setMembers] = useState<Member[]>([])
  const [newGroupName, setNewGroupName] = useState('')
  const [newMemberEmail, setNewMemberEmail] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    loadGroups()
  }, [])

  useEffect(() => {
    if (selectedGroup) {
      loadMembers()
    }
  }, [selectedGroup])

  const loadGroups = async () => {
    try {
      const data = await api.getGroups()
      setGroups(data)
      if (data.length > 0) {
        setSelectedGroup(data[0])
      }
    } catch (err) {
      console.error('Failed to load groups:', err)
    } finally {
      setLoading(false)
    }
  }

  const loadMembers = async () => {
    if (!selectedGroup) return
    try {
      const data = await api.getMembers(selectedGroup.id)
      setMembers(data)
    } catch (err) {
      console.error('Failed to load members:', err)
    }
  }

  const createGroup = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!newGroupName.trim()) return

    setError('')
    try {
      const group = await api.createGroup(newGroupName.trim())
      setGroups([...groups, group])
      setSelectedGroup(group)
      setNewGroupName('')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create group')
    }
  }

  const addMember = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!selectedGroup || !newMemberEmail.trim()) return

    setError('')
    try {
      const member = await api.addMember(selectedGroup.id, newMemberEmail.trim())
      setMembers([...members, member])
      setNewMemberEmail('')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to add member')
    }
  }

  const removeMember = async (userId: number) => {
    if (!selectedGroup) return

    try {
      await api.removeMember(selectedGroup.id, userId)
      setMembers(members.filter((m) => m.user_id !== userId))
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to remove member')
    }
  }

  if (loading) {
    return <div className="text-center text-gray-500">Loading...</div>
  }

  return (
    <div className="grid md:grid-cols-2 gap-8">
      {/* Left: Group list */}
      <div>
        <h2 className="text-xl font-bold mb-4">Your Groups</h2>

        <div className="bg-white rounded-lg border divide-y">
          {groups.length === 0 ? (
            <div className="p-4 text-gray-500 text-center">No groups yet</div>
          ) : (
            groups.map((group) => (
              <button
                key={group.id}
                onClick={() => setSelectedGroup(group)}
                className={`w-full p-4 text-left hover:bg-gray-50 flex items-center justify-between ${
                  selectedGroup?.id === group.id ? 'bg-indigo-50' : ''
                }`}
              >
                <span className="font-medium">{group.name}</span>
                {group.is_owner && (
                  <span className="text-xs text-indigo-600 bg-indigo-100 px-2 py-1 rounded">
                    Owner
                  </span>
                )}
              </button>
            ))
          )}
        </div>

        {/* Create new group */}
        <form onSubmit={createGroup} className="mt-4">
          <div className="flex gap-2">
            <input
              type="text"
              value={newGroupName}
              onChange={(e) => setNewGroupName(e.target.value)}
              placeholder="New group name"
              className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
            <button
              type="submit"
              className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
            >
              Create
            </button>
          </div>
        </form>
      </div>

      {/* Right: Group details / members */}
      <div>
        {selectedGroup ? (
          <>
            <h2 className="text-xl font-bold mb-4">{selectedGroup.name} - Members</h2>

            {error && (
              <div className="mb-4 p-3 bg-red-50 text-red-700 rounded-md text-sm">{error}</div>
            )}

            <div className="bg-white rounded-lg border divide-y">
              {members.map((member) => (
                <div key={member.id} className="p-4 flex items-center justify-between">
                  <div>
                    <div className="font-medium">{member.name}</div>
                    <div className="text-sm text-gray-500">{member.email}</div>
                  </div>
                  {selectedGroup.is_owner && member.user_id !== selectedGroup.owner_id && (
                    <button
                      onClick={() => removeMember(member.user_id)}
                      className="text-red-600 hover:text-red-800 text-sm"
                    >
                      Remove
                    </button>
                  )}
                </div>
              ))}
            </div>

            {/* Add member (owner only) */}
            {selectedGroup.is_owner && (
              <form onSubmit={addMember} className="mt-4">
                <div className="flex gap-2">
                  <input
                    type="email"
                    value={newMemberEmail}
                    onChange={(e) => setNewMemberEmail(e.target.value)}
                    placeholder="Member email"
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                  <button
                    type="submit"
                    className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
                  >
                    Add
                  </button>
                </div>
              </form>
            )}
          </>
        ) : (
          <div className="text-center text-gray-500 py-12">
            Select a group to view members
          </div>
        )}
      </div>
    </div>
  )
}

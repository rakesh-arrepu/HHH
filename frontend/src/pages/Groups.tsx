import { useState, useEffect } from 'react'
import { api } from '../api'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Users,
  Plus,
  Crown,
  Mail,
  UserPlus,
  UserMinus,
  Sparkles,
  UsersRound,
  ArrowRightLeft
} from 'lucide-react'
import {
  GlassCard,
  GlowButton,
  InputField,
  PageContainer,
  PageTitle,
  Badge,
  IconButton,
  EmptyState
} from '../components/ui'
import { sideCannons } from '../components/ui/confetti'

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
  const [creating, setCreating] = useState(false)
  const [adding, setAdding] = useState(false)
  const [transferring, setTransferring] = useState(false)
  const [showTransferModal, setShowTransferModal] = useState(false)

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
    setCreating(true)
    try {
      const group = await api.createGroup(newGroupName.trim())
      setGroups([...groups, group])
      setSelectedGroup(group)
      setNewGroupName('')
      sideCannons()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create group')
    } finally {
      setCreating(false)
    }
  }

  const addMember = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!selectedGroup || !newMemberEmail.trim()) return

    setError('')
    setAdding(true)
    try {
      const member = await api.addMember(selectedGroup.id, newMemberEmail.trim())
      setMembers([...members, member])
      setNewMemberEmail('')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to add member')
    } finally {
      setAdding(false)
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

  const transferOwnership = async (newOwnerId: number) => {
    if (!selectedGroup) return

    const newOwner = members.find((m) => m.user_id === newOwnerId)
    if (!newOwner) return

    if (!confirm(`Are you sure you want to transfer ownership to ${newOwner.name}? This action cannot be undone.`)) {
      return
    }

    setError('')
    setTransferring(true)
    try {
      await api.transferOwnership(selectedGroup.id, newOwnerId)

      // Update groups list
      setGroups(groups.map(g =>
        g.id === selectedGroup.id
          ? { ...g, owner_id: newOwnerId, is_owner: false }
          : g
      ))

      // Update selected group
      setSelectedGroup({ ...selectedGroup, owner_id: newOwnerId, is_owner: false })

      setShowTransferModal(false)

      // Show success message
      alert(`Ownership successfully transferred to ${newOwner.name}!`)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to transfer ownership')
    } finally {
      setTransferring(false)
    }
  }

  if (loading) {
    return (
      <PageContainer className="flex items-center justify-center min-h-[60vh]">
        <div className="spinner" />
      </PageContainer>
    )
  }

  return (
    <PageContainer>
      <PageTitle
        title="Groups"
        subtitle="Manage your tracking groups and members"
        icon={UsersRound}
      />

      <div className="grid lg:grid-cols-2 gap-6">
        {/* Left: Group list */}
        <div>
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.4 }}
          >
            <GlassCard>
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-lg font-semibold text-white flex items-center gap-2">
                  <Users className="w-5 h-5 text-purple-400" />
                  Your Groups
                </h2>
                <span className="text-white/40 text-sm">{groups.length} groups</span>
              </div>

              {groups.length === 0 ? (
                <div className="text-center py-8">
                  <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-white/5 flex items-center justify-center">
                    <Users className="w-8 h-8 text-white/30" />
                  </div>
                  <p className="text-white/50">No groups yet</p>
                  <p className="text-white/30 text-sm mt-1">Create one to get started</p>
                </div>
              ) : (
                <div className="space-y-2">
                  {groups.map((group, index) => (
                    <motion.button
                      key={group.id}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: index * 0.05 }}
                      onClick={() => setSelectedGroup(group)}
                      className={`w-full p-4 rounded-xl text-left transition-all duration-300 flex items-center justify-between group ${
                        selectedGroup?.id === group.id
                          ? 'bg-purple-500/20 border border-purple-500/30'
                          : 'bg-white/5 border border-white/10 hover:bg-white/10 hover:border-white/20'
                      }`}
                    >
                      <div className="flex items-center gap-3">
                        <div
                          className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                            selectedGroup?.id === group.id
                              ? 'bg-purple-500/30'
                              : 'bg-white/10 group-hover:bg-white/15'
                          }`}
                        >
                          <Sparkles
                            className={`w-5 h-5 ${
                              selectedGroup?.id === group.id
                                ? 'text-purple-400'
                                : 'text-white/50 group-hover:text-white/70'
                            }`}
                          />
                        </div>
                        <span
                          className={`font-medium ${
                            selectedGroup?.id === group.id
                              ? 'text-white'
                              : 'text-white/80 group-hover:text-white'
                          }`}
                        >
                          {group.name}
                        </span>
                      </div>
                      {group.is_owner && (
                        <Badge variant="owner" icon={Crown}>
                          Owner
                        </Badge>
                      )}
                    </motion.button>
                  ))}
                </div>
              )}

              {/* Create new group */}
              <form onSubmit={createGroup} className="mt-6 pt-6 border-t border-white/10">
                <div className="flex gap-3">
                  <div className="flex-1">
                    <InputField
                      type="text"
                      value={newGroupName}
                      onChange={(e) => setNewGroupName(e.target.value)}
                      placeholder="Enter group name"
                      icon={Plus}
                    />
                  </div>
                  <GlowButton
                    type="submit"
                    loading={creating}
                    disabled={!newGroupName.trim()}
                  >
                    Create
                  </GlowButton>
                </div>
              </form>
            </GlassCard>
          </motion.div>
        </div>

        {/* Right: Group details / members */}
        <div>
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.4, delay: 0.1 }}
          >
            <AnimatePresence mode="wait">
              {selectedGroup ? (
                <motion.div
                  key={selectedGroup.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                >
                  <GlassCard>
                    <div className="flex items-center justify-between mb-6">
                      <div>
                        <h2 className="text-lg font-semibold text-white">
                          {selectedGroup.name}
                        </h2>
                        <p className="text-white/50 text-sm">{members.length} members</p>
                      </div>
                      {selectedGroup.is_owner && (
                        <Badge variant="owner" icon={Crown}>
                          You're the owner
                        </Badge>
                      )}
                    </div>

                    {error && (
                      <motion.div
                        initial={{ opacity: 0, y: -10 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="mb-4 p-4 rounded-xl bg-red-500/10 border border-red-500/30"
                      >
                        <p className="text-red-400 text-sm">{error}</p>
                      </motion.div>
                    )}

                    {/* Members list */}
                    <div className="space-y-3">
                      {members.map((member, index) => (
                        <motion.div
                          key={member.id}
                          initial={{ opacity: 0, x: -10 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: index * 0.05 }}
                          className="flex items-center justify-between p-4 rounded-xl bg-white/5 border border-white/10"
                        >
                          <div className="flex items-center gap-3">
                            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center text-white font-medium">
                              {member.name.charAt(0).toUpperCase()}
                            </div>
                            <div>
                              <div className="font-medium text-white flex items-center gap-2">
                                {member.name}
                                {member.user_id === selectedGroup.owner_id && (
                                  <Crown className="w-4 h-4 text-amber-400" />
                                )}
                              </div>
                              <div className="text-sm text-white/50">{member.email}</div>
                            </div>
                          </div>
                          <div className="flex items-center gap-2">
                            {selectedGroup.is_owner &&
                              member.user_id !== selectedGroup.owner_id && (
                                <>
                                  <IconButton
                                    icon={ArrowRightLeft}
                                    variant="warning"
                                    size="sm"
                                    tooltip="Transfer ownership"
                                    onClick={() => transferOwnership(member.user_id)}
                                  />
                                  <IconButton
                                    icon={UserMinus}
                                    variant="danger"
                                    size="sm"
                                    tooltip="Remove member"
                                    onClick={() => removeMember(member.user_id)}
                                  />
                                </>
                              )}
                          </div>
                        </motion.div>
                      ))}
                    </div>

                    {/* Add member (owner only) */}
                    {selectedGroup.is_owner && (
                      <form
                        onSubmit={addMember}
                        className="mt-6 pt-6 border-t border-white/10"
                      >
                        <label className="block text-sm font-medium text-white/80 mb-3">
                          Add a new member
                        </label>
                        <div className="flex gap-3">
                          <div className="flex-1">
                            <InputField
                              type="email"
                              value={newMemberEmail}
                              onChange={(e) => setNewMemberEmail(e.target.value)}
                              placeholder="Enter email address"
                              icon={Mail}
                            />
                          </div>
                          <GlowButton
                            type="submit"
                            loading={adding}
                            disabled={!newMemberEmail.trim()}
                            icon={UserPlus}
                            variant="success"
                          >
                            Add
                          </GlowButton>
                        </div>
                      </form>
                    )}
                  </GlassCard>
                </motion.div>
              ) : (
                <motion.div
                  key="empty"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                >
                  <EmptyState
                    icon={Users}
                    title="Select a Group"
                    description="Choose a group from the list to view and manage its members"
                  />
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        </div>
      </div>
    </PageContainer>
  )
}

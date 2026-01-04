import { Eye, Users } from 'lucide-react'
import { SelectField, Badge } from './ui'

export type Member = {
  id: number
  user_id: number
  name: string
  email: string
}

interface MemberSelectorProps {
  members: Member[]
  selectedUserId: number | undefined
  onSelectUser: (userId: number | undefined) => void
  currentUserId: number
  isOwner: boolean
  label?: string
}

export function MemberSelector({
  members,
  selectedUserId,
  onSelectUser,
  currentUserId,
  isOwner,
  label = "View Data As"
}: MemberSelectorProps) {
  // Don't render if not owner
  if (!isOwner) return null

  const currentMember = members.find(m => m.user_id === currentUserId)
  const selectedMember = selectedUserId ? members.find(m => m.user_id === selectedUserId) : null

  const options = [
    { value: '', label: `My Data${currentMember ? ` (${currentMember.name})` : ''}` },
    ...members
      .filter(m => m.user_id !== currentUserId)
      .map(m => ({
        value: String(m.user_id),
        label: m.name
      }))
  ]

  const handleChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = e.target.value
    onSelectUser(value === '' ? undefined : Number(value))
  }

  return (
    <div className="space-y-2">
      <SelectField
        label={label}
        options={options}
        value={selectedUserId === undefined ? '' : String(selectedUserId)}
        onChange={handleChange}
        icon={Eye}
      />
      {selectedMember && (
        <Badge variant="warning" icon={Users}>
          Viewing: {selectedMember.name}
        </Badge>
      )}
    </div>
  )
}

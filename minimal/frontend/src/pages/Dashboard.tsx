import { useState, useEffect } from 'react'
import { api } from '../api'

type Group = { id: number; name: string; is_owner: boolean }

const SECTIONS = [
  { key: 'health', label: 'Health', emoji: '💪', color: 'bg-green-50 border-green-200' },
  { key: 'happiness', label: 'Happiness', emoji: '😊', color: 'bg-yellow-50 border-yellow-200' },
  { key: 'hela', label: 'Hela (Money)', emoji: '💰', color: 'bg-blue-50 border-blue-200' },
]

export default function Dashboard() {
  const [groups, setGroups] = useState<Group[]>([])
  const [selectedGroup, setSelectedGroup] = useState<number | null>(null)
  const [entries, setEntries] = useState<Record<string, string>>({})
  const [streak, setStreak] = useState(0)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState<string | null>(null)

  useEffect(() => {
    loadGroups()
  }, [])

  useEffect(() => {
    if (selectedGroup) {
      loadTodayEntries()
      loadStreak()
    }
  }, [selectedGroup])

  const loadGroups = async () => {
    try {
      const data = await api.getGroups()
      setGroups(data)
      if (data.length > 0) {
        setSelectedGroup(data[0].id)
      }
    } catch (err) {
      console.error('Failed to load groups:', err)
    } finally {
      setLoading(false)
    }
  }

  const loadTodayEntries = async () => {
    if (!selectedGroup) return
    try {
      const today = new Date().toISOString().split('T')[0]
      const data = await api.getEntries(selectedGroup, today)
      const entriesMap: Record<string, string> = {}
      data.forEach((e) => {
        entriesMap[e.section] = e.content
      })
      setEntries(entriesMap)
    } catch (err) {
      console.error('Failed to load entries:', err)
    }
  }

  const loadStreak = async () => {
    if (!selectedGroup) return
    try {
      const data = await api.getStreak(selectedGroup)
      setStreak(data.streak)
    } catch (err) {
      console.error('Failed to load streak:', err)
    }
  }

  const saveEntry = async (section: string, content: string) => {
    if (!selectedGroup || !content.trim()) return

    setSaving(section)
    try {
      await api.createEntry({
        group_id: selectedGroup,
        section,
        content: content.trim(),
      })
      setEntries((prev) => ({ ...prev, [section]: content.trim() }))
      loadStreak() // Refresh streak after saving
    } catch (err) {
      console.error('Failed to save entry:', err)
    } finally {
      setSaving(null)
    }
  }

  if (loading) {
    return <div className="text-center text-gray-500">Loading...</div>
  }

  if (groups.length === 0) {
    return (
      <div className="text-center py-12">
        <h2 className="text-xl font-semibold text-gray-700 mb-4">No Groups Yet</h2>
        <p className="text-gray-500 mb-4">Create a group to start tracking your daily entries.</p>
        <a
          href="/groups"
          className="inline-block px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
        >
          Create Group
        </a>
      </div>
    )
  }

  const completedCount = Object.keys(entries).length
  const isComplete = completedCount === 3

  return (
    <div>
      {/* Header with group selector and streak */}
      <div className="flex items-center justify-between mb-8">
        <div className="flex items-center gap-4">
          <select
            value={selectedGroup || ''}
            onChange={(e) => setSelectedGroup(Number(e.target.value))}
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            {groups.map((g) => (
              <option key={g.id} value={g.id}>
                {g.name}
              </option>
            ))}
          </select>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-3xl">🔥</span>
          <span className="text-2xl font-bold text-orange-500">{streak}</span>
          <span className="text-gray-500">day streak</span>
        </div>
      </div>

      {/* Progress bar */}
      <div className="mb-8">
        <div className="flex justify-between text-sm text-gray-600 mb-2">
          <span>Today's Progress</span>
          <span>{completedCount}/3 sections</span>
        </div>
        <div className="h-3 bg-gray-200 rounded-full overflow-hidden">
          <div
            className={`h-full transition-all duration-300 ${
              isComplete ? 'bg-green-500' : 'bg-indigo-500'
            }`}
            style={{ width: `${(completedCount / 3) * 100}%` }}
          />
        </div>
        {isComplete && (
          <p className="text-green-600 text-sm mt-2 text-center">
            🎉 All sections complete for today!
          </p>
        )}
      </div>

      {/* Entry cards */}
      <div className="grid gap-6">
        {SECTIONS.map((section) => (
          <EntryCard
            key={section.key}
            section={section}
            content={entries[section.key] || ''}
            onSave={(content) => saveEntry(section.key, content)}
            saving={saving === section.key}
          />
        ))}
      </div>
    </div>
  )
}

function EntryCard({
  section,
  content,
  onSave,
  saving,
}: {
  section: { key: string; label: string; emoji: string; color: string }
  content: string
  onSave: (content: string) => void
  saving: boolean
}) {
  const [text, setText] = useState(content)
  const [editing, setEditing] = useState(false)

  useEffect(() => {
    setText(content)
  }, [content])

  const hasContent = content.trim().length > 0
  const isDirty = text !== content

  const handleSave = () => {
    onSave(text)
    setEditing(false)
  }

  return (
    <div className={`p-6 rounded-lg border-2 ${section.color}`}>
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <span className="text-2xl">{section.emoji}</span>
          <h3 className="text-lg font-semibold">{section.label}</h3>
        </div>
        {hasContent && !editing && (
          <span className="text-green-600 text-sm">✓ Completed</span>
        )}
      </div>

      {editing || !hasContent ? (
        <div>
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder={`What did you do for ${section.label.toLowerCase()} today?`}
            className="w-full p-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 min-h-[100px]"
          />
          <div className="flex justify-end gap-2 mt-3">
            {hasContent && (
              <button
                onClick={() => {
                  setText(content)
                  setEditing(false)
                }}
                className="px-4 py-2 text-gray-600 hover:text-gray-800"
              >
                Cancel
              </button>
            )}
            <button
              onClick={handleSave}
              disabled={saving || !text.trim() || !isDirty}
              className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:opacity-50"
            >
              {saving ? 'Saving...' : 'Save'}
            </button>
          </div>
        </div>
      ) : (
        <div>
          <p className="text-gray-700 whitespace-pre-wrap">{content}</p>
          <button
            onClick={() => setEditing(true)}
            className="mt-3 text-sm text-indigo-600 hover:underline"
          >
            Edit
          </button>
        </div>
      )}
    </div>
  )
}

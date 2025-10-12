import React, { useState } from 'react'

export default function EntryForm() {
  const [content, setContent] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setIsLoading(true)

    // TODO: Implement actual entry creation with API
    console.log('Creating entry:', content)

    // Simulate API call
    setTimeout(() => {
      setIsLoading(false)
      setContent('')
      alert('Entry created successfully!')
    }, 1000)
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label htmlFor="content" className="block text-sm font-medium text-gray-700 mb-2">
          What did you accomplish today?
        </label>
        <textarea
          id="content"
          name="content"
          rows={4}
          className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          placeholder="Write about your daily progress, goals achieved, or reflections..."
          value={content}
          onChange={(e) => setContent(e.target.value)}
          required
        />
      </div>

      <div className="flex justify-between items-center">
        <span className="text-xs text-gray-500">
          {content.length}/500 characters
        </span>
        <button
          type="submit"
          disabled={isLoading || content.length === 0}
          className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isLoading ? 'Saving...' : 'Save Entry'}
        </button>
      </div>
    </form>
  )
}

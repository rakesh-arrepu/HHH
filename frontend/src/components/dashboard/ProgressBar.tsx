import React from 'react'

export default function ProgressBar() {
  const progress = 78 // Mock data - percentage complete for today

  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <h3 className="text-lg font-medium text-gray-900 mb-4">Today's Progress</h3>
      <div className="space-y-2">
        <div className="flex justify-between text-sm">
          <span className="text-gray-600">Completion</span>
          <span className="font-medium">{progress}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-3">
          <div
            className="bg-green-500 h-3 rounded-full transition-all duration-300"
            style={{ width: `${progress}%` }}
          ></div>
        </div>
        <div className="text-xs text-gray-500 text-center mt-2">
          {progress >= 100 ? '🎉 All done for today!' : `${100 - progress}% remaining`}
        </div>
      </div>
    </div>
  )
}

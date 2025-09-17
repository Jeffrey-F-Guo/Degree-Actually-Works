import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'

function App() {
  const [count, setCount] = useState(0)

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col items-center justify-center p-8">
      <div className="flex gap-8 mb-8">
        <a href="https://vite.dev" target="_blank" className="hover:opacity-80 transition-opacity">
          <img src={viteLogo} className="h-16 w-16" alt="Vite logo" />
        </a>
        <a href="https://react.dev" target="_blank" className="hover:opacity-80 transition-opacity">
          <img src={reactLogo} className="h-16 w-16 animate-spin" alt="React logo" />
        </a>
      </div>

      <h1 className="text-4xl font-bold text-gray-800 mb-8">Vite + React + Tailwind</h1>

      <div className="bg-white rounded-lg shadow-lg p-8 max-w-md w-full">
        <button
          onClick={() => setCount((count) => count + 1)}
          className="w-full bg-blue-500 hover:bg-blue-600 text-white font-semibold py-3 px-6 rounded-lg transition-colors duration-200 mb-4"
        >
          Count is {count}
        </button>

        <p className="text-gray-600 text-center mb-4">
          Edit <code className="bg-gray-100 px-2 py-1 rounded text-sm">src/App.tsx</code> and save to test HMR
        </p>

        <div className="text-center">
          <h2 className="text-2xl font-semibold text-red-600 mb-2">Hello World!</h2>
          <p className="text-green-600 font-medium">Tailwind CSS is working! 🎉</p>
        </div>
      </div>

      <p className="text-gray-500 text-center mt-8 max-w-md">
        Click on the Vite and React logos to learn more about these technologies.
      </p>
    </div>
  )
}

export default App

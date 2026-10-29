import { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import './App.css'

function App() {
  const [prompt, setPrompt] = useState('')
  const [workout, setWorkout] = useState(null)
  const [audioUrl, setAudioUrl] = useState(null)
  const [loading, setLoading] = useState(false)

  const generateWorkout = async (e) => {
    e.preventDefault()
    setLoading(true)
    setWorkout(null)
    setAudioUrl(null)

    try {
      const response = await fetch('http://127.0.0.1:8000/generate-workout', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt })
      })
      
      const data = await response.json()
      setWorkout(data.agent_response)
      setAudioUrl(`http://127.0.0.1:8000${data.audio_url}?t=${Date.now()}`)
    } catch (error) {
      setWorkout("Error connecting to the AI coach. Is the FastAPI backend running?")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app-container">
      <h1>⚡️ AI Fitness Coach</h1>
      <form onSubmit={generateWorkout}>
        <input 
          type="text" 
          placeholder="e.g., Give me a 15-minute bodyweight shoulder workout" 
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          disabled={loading}
        />
        <button type="submit" disabled={loading || !prompt}>
          {loading ? 'Generating...' : 'Get Workout'}
        </button>
      </form>
      {audioUrl && (
        <div className="audio-player">
          <h3>Coaching Audio:</h3>
          <audio controls src={audioUrl} autoPlay />
        </div>
      )}
      {workout && (
        <div className="workout-display">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>{workout}</ReactMarkdown>
        </div>
      )}
    </div>
  )
}

export default App
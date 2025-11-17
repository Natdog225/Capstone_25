import { useState } from 'react'
import './styles/App.css'

function App() {
  const [count, setCount] = useState(0)

  return (
    <div className="App">
      <header className="App-header">
        <h1>DineMetra</h1>
        <p className="tagline">Forecast. Prepare. Perform.</p>
        <div className="card">
          <button onClick={() => setCount((count) => count + 1)}>
            count is {count}
          </button>
          <p>
            Edit <code>src/App.jsx</code> and save to test HMR
          </p>
        </div>
        <p className="description">
          Restaurant prediction app - Predicting busyness based on sales data, weather, and events
        </p>
      </header>
    </div>
  )
}

export default App

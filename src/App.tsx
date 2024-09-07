import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'

function App() {
  const [count, setCount] = useState(0)

  return (
    <>
      <div className="flex w-[200em] h-[200em] border border-black p-4">
         <p> Hello, world! </p>
      </div>
    </>
  )
}

export default App

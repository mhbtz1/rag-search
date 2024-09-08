import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import Search from './components/search'

function App() {
  const [count, setCount] = useState(0)

  return (
    <>
      <div>
        <div className="flex justify-center items-center w-[90vw] h-[2em] p-5 mt-10 mb-40 text-15 text-black border-2 border-black">
          <p> Matthew's Search Engine </p>
        </div> 
        <div className="flex justify-center mb-50">
          <Search/>
        </div>
      </div>
    </>
  )
}

export default App

import { useState } from 'react';
import Login from './Login'
import MultimodalSearch from './MultimodalSearch'

export default function App() {
    const [token, setToken] = useState('')

    return (<div>
        {!token ? 
            (<Login onLogin={setToken}/>    
            ): <MultimodalSearch/>
        }
        </div>)
}
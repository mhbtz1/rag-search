import {useState} from 'react'
import search_icon from '../assets/search-engine-icon-free-vector.jpg'

export default function Search() {
    const [query, updateQuery] = useState("")    
    
    function handleQuery(event) {
        event.preventDefault()
        const value = event?.target.value;
        let nQuery = value
        updateQuery(nQuery);
        console.log("query is currently: ", nQuery);
    }

    let divComponent = <div className="border-2 border-black text-black"> <p> Test message </p> </div>
    return (
        <div>
            <div className="flex w-[50em] h-[2em] border-2 border-blue-500">
                <img src={search_icon} className='flex items-center w-[2em] h-[1.5em] mr-2'/>
                <input type="text" placeholder="Type here..." className="w-[95%] bg-white text-black" onInput={(event) => handleQuery(event)}/>
            </div>
            { query.length > 0 ? divComponent : <div></div>}
        </div>
    )
}
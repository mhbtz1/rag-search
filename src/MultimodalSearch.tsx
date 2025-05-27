import React, { useState } from 'react';


export default function MultimodalSearch() {
  const [query, setQuery] = useState('');
  const [topK, setTopK] = useState<string | null>(null);
  const [results, setResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  const handleSearch = async () => {
    setLoading(true);
    let curTopK = '5';

    if (topK){
      curTopK = topK;
    }

    const res = await fetch(`${import.meta.env.VITE_API_HOST}/search`, {
      method: 'POST',
      body: JSON.stringify({
        'query': query,
        'top_k': curTopK
      }),
      headers: {
        'Content-Type': 'application/json'
      }
    });
    const data = await res.json();
    setResults(data.documents);
    setLoading(false);
  };

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold text-gray-800">Multimodal Search</h2>

      <input
        type="text"
        className="w-full border p-2 rounded"
        placeholder="Enter text query"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
      />

      <input
      type="text"
      className="w-full border p-2-rounded"
      placeholder="Number of results (defaults to 5 if empty)"
      value={topK}
      onChange={(e) => setTopK(e.target.value)}/>

      <button
        className="w-full bg-blue-600 text-white rounded py-2 hover:bg-blue-700"
        onClick={handleSearch}
        disabled={loading}
      >
        {loading ? 'Searching...' : 'Search'}
      </button>

      <div className="pt-4">
        {results.length > 0 && (
          <div className="space-y-2">
            <h2 className="font-semibold text-black">Results:</h2>
            <ul className="list-disc list-inside space-y-1 text-sm">
              {results.map((res, i) => (
                <li key={i} className="text-black">{res.title || res}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}


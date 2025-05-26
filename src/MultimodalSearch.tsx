import React, { useState } from 'react';


export default function MultimodalSearch() {
  const [query, setQuery] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [results, setResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files?.[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleSearch = async () => {
    setLoading(true);
    const formData = new FormData();
    formData.append('query', query);
    if (file) formData.append('file', file);

    const res = await fetch(`${import.meta.env.BASE_URL}/search`, {
      method: 'POST',
      body: formData,
    });
    const data = await res.json();
    setResults(data.results);
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
        type="file"
        className="w-full"
        onChange={handleFileChange}
      />

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
            <h2 className="font-semibold">Results:</h2>
            <ul className="list-disc list-inside space-y-1 text-sm">
              {results.map((res, i) => (
                <li key={i}>{res.title || res}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}


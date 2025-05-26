import { useState } from 'react';
import { PaperClipIcon } from '@heroicons/react/20/solid';

export default function FileUpload() {
  const [file, setFile] = useState<File | null>(null);
  const [selectedModel, setSelectedModel] = useState('');
  const [status, setStatus] = useState<string | null>(null);

  const MODEL_OPTIONS = [
    { label: "Small", value: "small" },
    { label: "Large", value: "large" }
  ]

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!file || !selectedModel ) {
      setStatus("File and model_params are required.");
      return;
    }

    const formData = new FormData();
    formData.append('file', file);
    formData.append('model_params', new Blob([JSON.stringify({model_alias: selectedModel.join(',')})], { type: 'application/json' }));

    try {
      const res = await fetch(`${import.meta.env.VITE_API_HOST}/ingest_file`, {
        method: 'POST',
        body: formData,
      });

      const data = await res.json();
      if (res.ok) {
        setStatus("File ingested successfully.");
      } else {
        setStatus(`Error: ${data.error}`);
      }
    } catch (err: any) {
      setStatus(`Error: ${err.message}`);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700">
            Select Embedding Model
        </label>
        <div className="space-y-2">
            { MODEL_OPTIONS.map((option) => {
                return (<label key={option.value} className="flex items-center space-x-2 text-sm">
                    <input 
                        type="radio"
                        name="embedding-model"
                        value={option.value}
                        checked={selectedModel == (option.value)}
                        onChange={() => setSelectedModel(option.value)}
                        className="h-4 w-4 text-indigo-600 border-gray-300 rounded"
                    />
                    <span className="text-black"> {option.label} </span>
                </label>)
            })}
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">
          Upload file
        </label>
        <div className="mt-1 flex items-center">
          <label className="flex cursor-pointer items-center rounded-md bg-gray-100 px-3 py-2 text-sm text-gray-600 hover:bg-gray-200">
            <PaperClipIcon className="h-4 w-4 mr-2" />
            <span>{file ? file.name : "Choose file"}</span>
            <input
              type="file"
              className="hidden"
              onChange={(e) => {
                const f = e.target.files?.[0];
                if (f) setFile(f);
              }}
              accept=".pdf,.csv,.xlsx,.docx"
              required
            />
          </label>
        </div>
      </div>

      {status && <p className="text-sm text-gray-500">{status}</p>}

      <div className="mt-4 flex justify-end">
        <button
          type="submit"
          className="rounded-md bg-indigo-600 px-4 py-2 text-sm text-white hover:bg-indigo-500"
        >
          Submit
        </button>
      </div>
    </form>
  );
}

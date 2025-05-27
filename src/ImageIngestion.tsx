import { useState } from 'react';

export default function ImageUpload() {
  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] = useState<string | null>(null);
  const [selectedModel, setSelectedModel] = useState('');

  const MODEL_OPTIONS = [
    { label: "Small", value: "small" },
    { label: "Large", value: "large" }
  ]
  
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0];
    if (f) setFile(f);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) {
      setStatus("Please select an image.");
      return;
    }

    const formData = new FormData();
    formData.append('image_file', file);
    formData.append('model_params', selectedModel);

    try {
      const res = await fetch(`${import.meta.env.VITE_API_HOST}/ingest_image`, {
        method: 'POST',
        body: formData,
      });
      const data = await res.json();

      if (res.ok) {
        setStatus('Image ingested successfully.');
      } else {
        setStatus(`Error: ${data.error}`);
      }
    } catch (err: any) {
      setStatus('Error uploading image.');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4 p-4 bg-white shadow rounded-md">
      <label className="block text-sm font-medium text-gray-700">Upload an image</label>
      <input type="file" accept="image/*" onChange={handleFileChange} className="text-sm" />

      {file && (
        <div className="mt-2">
          <img
            src={URL.createObjectURL(file)}
            alt="preview"
            className="max-w-xs rounded shadow"
          />
        </div>
      )}
 
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

      <button
        type="submit"
        className="mt-4 bg-indigo-600 text-white px-4 py-2 rounded hover:bg-indigo-500"
      >
        Submit
      </button>

      {status && <p className="text-sm text-gray-600">{status}</p>}
    </form>
  );
}

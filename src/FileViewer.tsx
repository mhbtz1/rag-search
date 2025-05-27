/*
import { useState } from 'react';

export default function FileStatusViewer() {
  const [fileId, setFileId] = useState('');
  const [status, setStatus] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleCheckStatus = async () => {
    if (!fileId) {
      setError('Please enter a file ID.');
      return;
    }

    setLoading(true);
    setStatus(null);
    setError(null);

    try {
      const res = await fetch(`${import.meta.env.VITE_API_HOST}/file_status/${fileId}`);
      const data = await res.json();

      if (res.ok) {
        setStatus(data.status);
      } else {
        setError(data.status || 'Error fetching status.');
      }
    } catch (err: any) {
      setError('Network error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-md mx-auto p-6 bg-white rounded-lg shadow space-y-4">
      <h2 className="text-lg font-bold text-gray-800">Check File Status</h2>

      <div>
        <label className="block text-sm font-medium text-gray-700">File ID</label>
        <input
          type="text"
          value={fileId}
          onChange={(e) => setFileId(e.target.value)}
          className="mt-1 w-full border border-gray-300 rounded px-3 py-2 text-sm"
          placeholder="Enter file ID (integer)"
        />
      </div>

      <button
        onClick={handleCheckStatus}
        className="w-full bg-indigo-600 text-white py-2 rounded hover:bg-indigo-500 text-sm"
        disabled={loading}
      >
        {loading ? 'Checking...' : 'Check Status'}
      </button>

      {status && (
        <p className="text-sm text-green-600">
          ✅ Status: <strong>{status}</strong>
        </p>
      )}

      {error && (
        <p className="text-sm text-red-600">
          ❌ {error}
        </p>
      )}
    </div>
  );
}
*/

import { useState, useRef, useEffect } from 'react';

export default function FileStatusViewer() {
  const [fileId, setFileId] = useState('');
  const [status, setStatus] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  const fetchStatus = async () => {
    try {
      const res = await fetch(`${import.meta.env.VITE_API_HOST}/file_status/${fileId}`);
      const data = await res.json();

      if (res.ok) {
        const newStatus = data.status;
        setStatus(newStatus);

        const terminalStates = ['FINISHED', 'ERROR', 'FAILED', 'success'];

        if (terminalStates.includes(newStatus.toUpperCase()) && intervalRef.current) {
          clearInterval(intervalRef.current);
          intervalRef.current = null;
        }
      } else {
        setError(data.status || 'Unknown error occurred.');
        if (intervalRef.current) {
          clearInterval(intervalRef.current);
          intervalRef.current = null;
        }
      }
    } catch (err: any) {
      setError('Network error');
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    } finally {
      setLoading(false);
    }
  };

  const handleCheckStatus = () => {
    if (!fileId) {
      setError('Please enter a file ID.');
      return;
    }

    setStatus(null);
    setError(null);
    setLoading(true);

    // Clear existing interval
    if (intervalRef.current) clearInterval(intervalRef.current);

    fetchStatus(); // Initial request

    // Start polling
    intervalRef.current = setInterval(() => {
      fetchStatus();
    }, 5000);
  };

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, []);

  return (
    <div className="max-w-md mx-auto p-6 bg-white rounded-lg shadow space-y-4">
      <h2 className="text-lg font-bold text-gray-800">Check File Status</h2>

      <div>
        <label className="block text-sm font-medium text-gray-700">File ID</label>
        <input
          type="text"
          value={fileId}
          onChange={(e) => setFileId(e.target.value)}
          className="mt-1 w-full border border-gray-300 rounded px-3 py-2 text-sm"
          placeholder="Enter file ID (integer)"
        />
      </div>

      <button
        onClick={handleCheckStatus}
        className="w-full bg-indigo-600 text-white py-2 rounded hover:bg-indigo-500 text-sm"
        disabled={loading && !status}
      >
        {loading && !status ? 'Checking...' : 'Check Status'}
      </button>

      {status && (
        <p className="text-sm text-blue-700">
          📄 <strong>Status:</strong> {status}
        </p>
      )}

      {error && (
        <p className="text-sm text-red-600">
          ❌ {error}
        </p>
      )}
    </div>
  );
}

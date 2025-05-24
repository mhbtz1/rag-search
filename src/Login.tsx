import { useState } from 'react';
import { Dialog } from '@headlessui/react';

export default function Login({ onLogin }: { onLogin: (token: string) => void }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleLogin = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      });

      const data = await response.json();
      if (response.ok && data.token) {
        onLogin(data.token);
      } else {
        setError('Invalid credentials or error logging in.');
      }
    } catch (err) {
      setError('Server error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center px-4">
      <div className="w-full max-w-sm">
        <Dialog open={true} onClose={() => {}}>
          <Dialog.Panel className="bg-white rounded-2xl shadow-lg p-6 space-y-4">
            <Dialog.Title className="text-lg font-medium text-gray-900">Login</Dialog.Title>

            <input
              type="text"
              placeholder="Username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full border border-gray-300 p-2 rounded"
            />

            <input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full border border-gray-300 p-2 rounded"
            />

            <button
              onClick={handleLogin}
              disabled={loading}
              className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700"
            >
              {loading ? 'Logging in...' : 'Login'}
            </button>

            {error && <p className="text-red-500 text-sm">{error}</p>}
          </Dialog.Panel>
        </Dialog>
      </div>
    </div>
  );
}

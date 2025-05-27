import { useState } from 'react';

interface AuthFormProps {
  onAuthSuccess: (token?: string) => void;
}

export default function AuthForm({ onAuthSuccess }: AuthFormProps) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [mode, setMode] = useState<'login' | 'register'>('login');
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const endpoint = mode === 'login' ? 'login' : 'register';

    try {
      const res = await fetch(`${import.meta.env.VITE_API_HOST}/${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      });

      const data = await res.json();

      if (res.ok) {
        if (mode === 'register' && data.status === 'success') {
          // Proceed even without token; you may generate one server-side later
          onAuthSuccess();
        } else if (mode === 'login' && data.token) {
          localStorage.setItem('authToken', data.token);
          onAuthSuccess(data.token);
        } else {
          setError('Unexpected response from server.');
        }
      } else {
        setError(data.error || 'Authentication failed');
      }
    } catch (err: any) {
      setError('Network error');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="max-w-sm mx-auto p-6 bg-white rounded-lg shadow space-y-4">
      <h2 className="text-lg font-bold text-gray-800">
        {mode === 'login' ? 'Login' : 'Register'}
      </h2>

      {error && <p className="text-sm text-red-500">{error}</p>}

      <div>
        <label className="block text-sm font-medium text-gray-700">Username</label>
        <input
          type="text"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          className="mt-1 w-full border border-gray-300 rounded px-3 py-2 text-sm"
          required
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">Password</label>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="mt-1 w-full border border-gray-300 rounded px-3 py-2 text-sm"
          required
        />
      </div>

      <button
        type="submit"
        className="w-full bg-indigo-600 text-white py-2 rounded hover:bg-indigo-500 text-sm"
      >
        {mode === 'login' ? 'Log In' : 'Create Account'}
      </button>

      <div className="text-sm text-center pt-2">
        {mode === 'login' ? (
          <>
            Don't have an account?{' '}
            <button
              type="button"
              onClick={() => {
                setError(null);
                setMode('register');
              }}
              className="text-indigo-600 hover:underline"
            >
              Register
            </button>
          </>
        ) : (
          <>
            Already have an account?{' '}
            <button
              type="button"
              onClick={() => {
                setError(null);
                setMode('login');
              }}
              className="text-indigo-600 hover:underline"
            >
              Log In
            </button>
          </>
        )}
      </div>
    </form>
  );
}

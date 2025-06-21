/* eslint-disable @typescript-eslint/no-explicit-any */
import { MediguardApi } from '@/app/services';
import { useState } from 'react';
import { useNavigate } from 'react-router';
import AuthLayout from './AuthLayout';

export default function LoginPage () {
  const mediguardApi= new MediguardApi(false, false, true);
  const navigate = useNavigate();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);  // ✅ Loading state

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await mediguardApi.authApi.login({ email, password });
      console.log("Login response:", response);

      const { user, tokens } = response.data;
      console.log("User logged in:", user);
      await mediguardApi.baseApi.storeTokens(tokens)
      await mediguardApi.baseApi.storeUser(user)


      navigate('/dashboard');
    } catch (err:any) {
      console.error(err);
      setError(err.response?.data?.detail || "Invalid credentials.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthLayout>
      <h2 className="text-3xl font-bold mb-6 text-center">Login</h2>

      {error && <p className="text-red-600 text-sm text-center mb-3">{error}</p>}

      <form className="space-y-5" onSubmit={handleSubmit}>
        <div>
          <label className="block mb-1 font-medium">Email</label>
          <input 
            type="email" 
            className="w-full border border-gray-300 rounded-lg p-3 focus:outline-none focus:ring-2 focus:ring-blue-400" 
            placeholder="Enter your email" 
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
        </div>

        <div>
          <label className="block mb-1 font-medium">Password</label>
          <input 
            type="password" 
            className="w-full border border-gray-300 rounded-lg p-3 focus:outline-none focus:ring-2 focus:ring-blue-400" 
            placeholder="Enter your password" 
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </div>

        <button 
          type="submit" 
          className={`w-full p-3 rounded-lg font-semibold transition ${loading ? 'bg-blue-300 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-700 text-white'}`}
          disabled={loading}
        >
          {loading ? 'Loading...' : 'Login'}
        </button>
      </form>

      <div className="mt-5 text-center text-sm text-gray-600">
        Don't remember your password?{' '}
        <button onClick={() => navigate('/forgot-password')} className="text-blue-600 hover:underline">
          Reset it here
        </button>
      </div>

      <div className="mt-2 text-center text-sm text-gray-600">
        Don't have an account?{' '}
        <button onClick={() => navigate('/signup')} className="text-blue-600 hover:underline">
          Sign up now
        </button>
      </div>
    </AuthLayout>
  );
}

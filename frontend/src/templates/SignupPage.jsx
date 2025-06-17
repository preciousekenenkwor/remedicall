import React, { useState } from 'react';
import AuthLayout from './AuthLayout';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

export default function SignupPage() {
  const navigate = useNavigate();

  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);  // ✅ Loading state

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    try {
      setLoading(true);

      const response = await axios.post('http://localhost:8000/signup', {
        full_name: fullName,
        email: email,
        password: password
      });

      console.log('User created:', response.data);

      navigate(`/verify-register?email=${encodeURIComponent(email)}`);
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || "Something went wrong.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthLayout>
      <h2 className="text-3xl font-bold mb-6 text-center">Sign Up</h2>

      {error && <p className="text-red-600 text-sm text-center mb-3">{error}</p>}

      <form className="space-y-5" onSubmit={handleSubmit}>
        <div>
          <label className="block mb-1 font-medium">Full Name</label>
          <input 
            type="text" 
            className="w-full border border-gray-300 rounded-lg p-3 focus:outline-none focus:ring-2 focus:ring-blue-400" 
            placeholder="Enter your full name" 
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
          />
        </div>

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

        <div>
          <label className="block mb-1 font-medium">Confirm Password</label>
          <input 
            type="password" 
            className="w-full border border-gray-300 rounded-lg p-3 focus:outline-none focus:ring-2 focus:ring-blue-400" 
            placeholder="Confirm your password" 
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
          />
        </div>

        <button 
          type="submit" 
          disabled={loading}
          className={`w-full p-3 rounded-lg font-semibold transition 
            ${loading ? 'bg-blue-300 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-700 text-white'}`}
        >
          {loading ? 'Creating...' : 'Create Account'}
        </button>
      </form>

      <div className="mt-5 text-sm text-center text-gray-600">
        Already have an account?{' '}
        <button onClick={() => navigate('/login')} className="text-blue-600 hover:underline">
          Login here
        </button>
      </div>
    </AuthLayout>
  );
}

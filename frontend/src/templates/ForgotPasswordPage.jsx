import React, { useState } from 'react';
import AuthLayout from './AuthLayout';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

export default function ForgotPasswordPage() {
  const navigate = useNavigate();

  const [email, setEmail] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false); // ✅ Loading state

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    try {
      setLoading(true);

      await axios.post('http://localhost:8000/forgot-password', {
        email: email,
        code: "" 
      });

      sessionStorage.setItem('resetEmail', email);
      setSuccess("Verification code sent! Please check your email.");
      setTimeout(() => {
        navigate('/verify-forgot-password');
      }, 1500);
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || "Something went wrong.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthLayout>
      <h2 className="text-3xl font-bold mb-6 text-center">Forgot Password</h2>

      <p className="text-center text-sm text-gray-600 mb-5">
        Enter your email address and we will send you a verification code to reset your password.
      </p>

      {error && <p className="text-red-600 text-sm text-center mb-3">{error}</p>}
      {success && <p className="text-green-600 text-sm text-center mb-3">{success}</p>}

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

        <button 
          type="submit" 
          disabled={loading}
          className={`w-full p-3 rounded-lg font-semibold transition 
            ${loading ? 'bg-blue-300 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-700 text-white'}`}
        >
          {loading ? 'Sending...' : 'Send Verification Code'}
        </button>
      </form>

      <div className="mt-5 text-sm text-center text-gray-600">
        Remember your password?{' '}
        <button onClick={() => navigate('/login')} className="text-blue-600 hover:underline">
          Login here
        </button>
      </div>
    </AuthLayout>
  );
}

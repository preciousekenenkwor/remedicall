import React, { useState } from 'react';
import AuthLayout from './AuthLayout';
import { useNavigate, useLocation } from 'react-router-dom';
import axios from 'axios';

export default function VerifyRegisterPage() {
  const navigate = useNavigate();
  const location = useLocation();

  const queryParams = new URLSearchParams(location.search);
  const email = queryParams.get('email');

  const [code, setCode] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false); // ✅ Loading state

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!email) {
      setError("No email provided. Please sign up again.");
      return;
    }

    try {
      setLoading(true);

      await axios.post('http://localhost:8000/verify-email', {
        email: email,
        code: code
      });

      navigate('/login');
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || "Invalid code.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthLayout>
      <h2 className="text-3xl font-bold mb-6 text-center">Verify Your Account</h2>

      <p className="text-center text-sm text-gray-600 mb-5">
        Enter the 6-digit code we sent to your email address.
      </p>

      {error && <p className="text-red-600 text-sm text-center mb-3">{error}</p>}

      <form className="space-y-5" onSubmit={handleSubmit}>
        <div>
          <label className="block mb-1 font-medium">Verification Code</label>
          <input 
            type="text" 
            maxLength="6"
            className="w-full border border-gray-300 rounded-lg p-3 text-center tracking-widest text-xl focus:outline-none focus:ring-2 focus:ring-blue-400" 
            placeholder="______" 
            value={code}
            onChange={(e) => setCode(e.target.value)}
          />
        </div>

        <button 
          type="submit" 
          disabled={loading}
          className={`w-full p-3 rounded-lg font-semibold transition 
            ${loading ? 'bg-blue-300 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-700 text-white'}`}
        >
          {loading ? 'Verifying...' : 'Verify Account'}
        </button>
      </form>

      <div className="mt-5 text-sm text-center text-gray-600">
        Didn't receive code?{' '}
        <button onClick={() => navigate('/signup')} className="text-blue-600 hover:underline">
          Resend Code
        </button>
      </div>
    </AuthLayout>
  );
}

import React, { useState } from 'react';
import AuthLayout from './AuthLayout';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

export default function VerifyForgotPasswordPage() {
  const navigate = useNavigate();

  const [code, setCode] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);  // ✅ Loading state

  const email = sessionStorage.getItem('resetEmail');

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!email) {
      setError("Missing email. Please restart the process.");
      return;
    }

    try {
      setLoading(true);

      await axios.post('http://localhost:8000/verify-reset-code', {
        email: email,
        code: code
      });

      sessionStorage.setItem('resetCode', code);

      setSuccess("Code verified! Redirecting...");
      setTimeout(() => {
        navigate('/reset-password');
      }, 1000);
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || "Invalid code.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthLayout>
      <h2 className="text-3xl font-bold mb-6 text-center">Verify Reset Code</h2>

      <p className="text-center text-sm text-gray-600 mb-5">
        Enter the 6-digit code we just sent to your email.
      </p>

      {error && <p className="text-red-600 text-sm text-center mb-3">{error}</p>}
      {success && <p className="text-green-600 text-sm text-center mb-3">{success}</p>}

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
          {loading ? 'Verifying...' : 'Verify Code'}
        </button>
      </form>

      <div className="mt-5 text-sm text-center text-gray-600">
        Didn't receive code?{' '}
        <button onClick={() => navigate('/forgot-password')} className="text-blue-600 hover:underline">
          Resend Code
        </button>
      </div>
    </AuthLayout>
  );
}

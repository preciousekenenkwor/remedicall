import React, { useState } from 'react';
import AuthLayout from './AuthLayout';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

export default function ResetPasswordPage() {
  const navigate = useNavigate();

  const email = sessionStorage.getItem('resetEmail');
  const code = sessionStorage.getItem('resetCode');

  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);  // ✅ Loading state

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!email || !code) {
      setError("Missing email or code. Please request a new reset.");
      return;
    }

    if (newPassword !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    try {
      setLoading(true);

      await axios.post('http://localhost:8000/reset-password', {
        email: email,
        code: code,
        new_password: newPassword
      });

      sessionStorage.removeItem('resetEmail');
      sessionStorage.removeItem('resetCode');

      setSuccess("Password reset successfully! Redirecting...");
      setTimeout(() => {
        navigate('/login');
      }, 1500);
    } catch (err) {
      console.error(err);
      const detail = err.response?.data?.detail;
      const errMsg = Array.isArray(detail)
        ? detail[0]?.msg
        : detail || "Something went wrong.";
      setError(errMsg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthLayout>
      <h2 className="text-3xl font-bold mb-6 text-center">Reset Password</h2>

      <p className="text-center text-sm text-gray-600 mb-5">
        Enter your new password below.
      </p>

      {error && <p className="text-red-600 text-sm text-center mb-3">{error}</p>}
      {success && <p className="text-green-600 text-sm text-center mb-3">{success}</p>}

      <form className="space-y-5" onSubmit={handleSubmit}>
        <div>
          <label className="block mb-1 font-medium">New Password</label>
          <input 
            type="password" 
            className="w-full border border-gray-300 rounded-lg p-3 focus:outline-none focus:ring-2 focus:ring-blue-400" 
            placeholder="Enter new password" 
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
          />
        </div>

        <div>
          <label className="block mb-1 font-medium">Confirm New Password</label>
          <input 
            type="password" 
            className="w-full border border-gray-300 rounded-lg p-3 focus:outline-none focus:ring-2 focus:ring-blue-400" 
            placeholder="Confirm new password" 
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
          {loading ? 'Resetting...' : 'Reset Password'}
        </button>
      </form>

      <div className="mt-5 text-sm text-center text-gray-600">
        Already reset your password?{' '}
        <button onClick={() => navigate('/login')} className="text-blue-600 hover:underline">
          Login here
        </button>
      </div>
    </AuthLayout>
  );
}

import React from 'react';
import { useNavigate } from 'react-router-dom';
import logo from '../images/logo.png'; // ✅ your RemediCall logo

export default function DashboardPage() {
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('userEmail');
    navigate('/login');
  };

  const email = localStorage.getItem('userEmail');

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-700 to-cyan-500 text-white flex flex-col">
      
      {/* Header */}
      <header className="flex items-center justify-between p-4 shadow-md bg-blue-900">
        <div className="flex items-center">
          <img src={logo} alt="RemediCall Logo" className="h-12 w-12 mr-3" />
          <h1 className="text-2xl font-bold">RemediCall</h1>
        </div>
        <div className="flex items-center space-x-4">
          <span className="text-sm hidden md:block">{email}</span>
          <button onClick={handleLogout} className="bg-white text-blue-700 px-4 py-2 rounded-lg font-semibold hover:bg-gray-100 transition">
            Logout
          </button>
        </div>
      </header>

      {/* Main Dashboard */}
      <main className="flex-grow p-6 flex flex-col items-center justify-center space-y-8">

        <h2 className="text-3xl font-extrabold drop-shadow-lg text-center">Welcome back!</h2>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 w-full max-w-4xl">

          <div className="bg-white text-blue-800 rounded-xl shadow-lg p-6 flex flex-col items-center justify-center hover:scale-105 transition">
            <h3 className="text-xl font-bold mb-4">Today's Medications</h3>
            <p className="text-5xl font-extrabold">3</p>
            <p className="mt-2 text-sm text-gray-600">Remaining doses today</p>
          </div>

          <div className="bg-white text-blue-800 rounded-xl shadow-lg p-6 flex flex-col items-center justify-center hover:scale-105 transition">
            <h3 className="text-xl font-bold mb-4">Next Reminder</h3>
            <p className="text-3xl font-extrabold">2:00 PM</p>
            <p className="mt-2 text-sm text-gray-600">Paracetamol 500mg</p>
          </div>

          <div className="bg-white text-blue-800 rounded-xl shadow-lg p-6 flex flex-col items-center justify-center hover:scale-105 transition">
            <h3 className="text-xl font-bold mb-4">Location</h3>
            <p className="text-lg font-bold">Kitchen Cabinet</p>
            <p className="mt-2 text-sm text-gray-600">Medication stored</p>
          </div>

        </div>

        <div className="flex space-x-6">
          <button className="bg-white text-blue-700 font-semibold px-6 py-3 rounded-lg shadow-lg hover:bg-gray-100 transition">
            ➕ Add Medication
          </button>
          <button className="bg-white text-blue-700 font-semibold px-6 py-3 rounded-lg shadow-lg hover:bg-gray-100 transition">
            🗂 Manage Medications
          </button>
        </div>

      </main>
    </div>
  );
}

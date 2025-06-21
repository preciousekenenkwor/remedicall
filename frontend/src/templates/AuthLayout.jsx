import React from 'react';
import oldWoman from '../images/old.jpg';

export default function AuthLayout({ children }) {
  return (
    <div 
      className="min-h-screen flex items-center justify-center text-white relative bg-gradient-to-br from-blue-700 to-cyan-500"
      style={{
        backgroundImage: `url(${oldWoman})`,
        backgroundSize: 'cover',
        backgroundPosition: 'center',
      }}
    >
      {/* Overlay */}
      <div className="absolute inset-0 bg-gradient-to-br from-blue-900/80 to-cyan-700/60 z-0"></div>

      {/* Auth Container */}
      <div className="relative z-10 bg-white rounded-2xl shadow-2xl p-10 w-full max-w-md text-gray-800 animate-fade-in">
        {children}
      </div>
    </div>
  );
}

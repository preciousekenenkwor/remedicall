import React from 'react';
import ReactDOM from 'react-dom/client';
import { HashRouter as Router, Routes, Route } from 'react-router-dom';

import HomePage from './templates/HomePage';
import LoginPage from './templates/LoginPage';
import SignupPage from './templates/SignupPage';
import VerifyRegisterPage from './templates/VerifyRegisterPage';
import ForgotPasswordPage from './templates/ForgotPasswordPage';
import VerifyForgotPasswordPage from './templates/VerifyForgotPasswordPage';
import ResetPasswordPage from './templates/ResetPasswordPage';
import DashboardPage from './templates/DashboardPage';
import PrivateRoute from './templates/PrivateRoute';

import './index.css';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/signup" element={<SignupPage />} />
        <Route path="/verify-register" element={<VerifyRegisterPage />} />
        <Route path="/forgot-password" element={<ForgotPasswordPage />} />
        <Route path="/verify-forgot-password" element={<VerifyForgotPasswordPage />} />
        <Route path="/reset-password" element={<ResetPasswordPage />} />

        {/* 🔐 Protected Route */}
        <Route 
          path="/dashboard" 
          element={
            <PrivateRoute>
              <DashboardPage />
            </PrivateRoute>
          } 
        />
      </Routes>
    </Router>
  </React.StrictMode>
);

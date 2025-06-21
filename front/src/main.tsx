import React from "react";
import ReactDOM from "react-dom/client";
import { Route, HashRouter as Router, Routes } from "react-router";
import "./index.css";

import { Provider } from "react-redux";
import store from "./app/store";
import DashboardPage from "./pages/DashboardPage";
import ForgotPasswordPage from "./pages/ForgotPasswordPage";
import HomePage from "./pages/HomePage";
import LoginPage from "./pages/LoginPage";
import PrivateRoute from "./pages/PrivateRoute";
import ResetPasswordPage from "./pages/ResetPasswordPage";
import SignupPage from "./pages/SignupPage";
import VerifyForgotPasswordPage from "./pages/VerifyForgotPasswordPage";
import VerifyRegisterPage from "./pages/VerifyRegisterPage";
import ToastProvider from "./utils/toaster";

const root = ReactDOM.createRoot(
  document.getElementById("root") as HTMLElement
);
root.render(
  <React.StrictMode>
    <Provider store={store}>
      <ToastProvider/>
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/signup" element={<SignupPage />} />
        <Route path="/verify-register" element={<VerifyRegisterPage />} />
        <Route path="/forgot-password" element={<ForgotPasswordPage />} />
        <Route
          path="/verify-forgot-password"
          element={<VerifyForgotPasswordPage />}
        />
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
    </Provider>
  </React.StrictMode>
);

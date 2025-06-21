/* eslint-disable @typescript-eslint/no-explicit-any */
import { AppConfig } from "@/app/config";
import { MediguardApi } from "@/app/services";
import { errorToast, successToast } from "@/utils/toaster";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router";
import AuthLayout from "./AuthLayout";

export default function VerifyForgotPasswordPage() {
  const navigate = useNavigate();

  const [code, setCode] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);
  const [resendLoading, setResendLoading] = useState(false);
  const [resendTimeout, setResendTimeout] = useState(0);

  const email = sessionStorage.getItem(AppConfig.RESET_EMAIL_KEY);

  const mediguardApi = new MediguardApi(false, false, true);

  // Timer effect for resend timeout
  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (resendTimeout > 0) {
      interval = setInterval(() => {
        setResendTimeout((prev) => prev - 1);
      }, 1000);
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [resendTimeout]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!email) {
      setError("Missing email. Please restart the process.");
      return;
    }

    try {
      setLoading(true);
      setError("");
      setSuccess("");

      const response = await mediguardApi.authApi.verifyForgotPasswordToken(
        code, email
      );
      console.log({response})
      successToast(String(response.message));

      sessionStorage.setItem(AppConfig.RESET_TOKEN_KEY, code);

      setSuccess("Code verified! Redirecting...");
      setTimeout(() => {
        navigate("/reset-password");
      }, 1000);
    } catch (err: any) {
      console.error(err);
      errorToast(err.detail?.message || "Invalid token or token has expired.");
      setError(err.detail?.message || "Invalid code.");
    } finally {
      setLoading(false);
    }
  };

  const handleResendCode = async () => {
    if (resendTimeout > 0 || resendLoading) return;

    try {
      setResendLoading(true);
      setError("");
      setSuccess("");

      const response = await mediguardApi.authApi.forgotPassword(email || "");
      successToast(response.data);
      setSuccess("Verification code sent! Please check your email.");

      // Set 60-second timeout before allowing another resend
      setResendTimeout(60);
    } catch (err: any) {
      console.error(err);
      errorToast(err.detail?.message || "Something went wrong.");
      setError(err.response?.data?.detail || "Something went wrong.");
    } finally {
      setResendLoading(false);
    }
  };

  const formatTime = (seconds: number) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, "0")}`;
  };

  return (
    <AuthLayout>
      <h2 className="text-3xl font-bold mb-6 text-center">Verify Reset Code</h2>

      <p className="text-center text-sm text-gray-600 mb-5">
        Enter the 6-digit code we just sent to your email.
      </p>

      {error && (
        <p className="text-red-600 text-sm text-center mb-3">{error}</p>
      )}
      {success && (
        <p className="text-green-600 text-sm text-center mb-3">{success}</p>
      )}

      <form className="space-y-5" onSubmit={handleSubmit}>
        <div>
          <label className="block mb-1 font-medium">Verification Code</label>
          <input
            type="text"
            maxLength={6}
            className="w-full border border-gray-300 rounded-lg p-3 text-center tracking-widest text-xl focus:outline-none focus:ring-2 focus:ring-blue-400"
            placeholder="______"
            value={code}
            onChange={(e) => setCode(e.target.value)}
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className={`w-full p-3 rounded-lg font-semibold transition flex items-center justify-center
            ${
              loading
                ? "bg-blue-300 cursor-not-allowed"
                : "bg-blue-600 hover:bg-blue-700 text-white"
            }`}
        >
          {loading && (
            <svg
              className="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              ></circle>
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              ></path>
            </svg>
          )}
          {loading ? "Verifying..." : "Verify Code"}
        </button>
      </form>

      <div className="mt-5 text-sm text-center text-gray-600">
        Didn't receive code?{" "}
        <button
          onClick={handleResendCode}
          disabled={resendTimeout > 0 || resendLoading}
          className={`inline-flex items-center ${
            resendTimeout > 0 || resendLoading
              ? "text-gray-400 cursor-not-allowed"
              : "text-blue-600 hover:underline"
          }`}
        >
          {resendLoading && (
            <svg
              className="animate-spin -ml-1 mr-1 h-4 w-4"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              ></circle>
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              ></path>
            </svg>
          )}
          {resendTimeout > 0
            ? `Resend Code (${formatTime(resendTimeout)})`
            : resendLoading
            ? "Sending..."
            : "Resend Code"}
        </button>
      </div>
    </AuthLayout>
  );
}

/* eslint-disable @typescript-eslint/no-explicit-any */
import { MediguardApi } from "@/app/services";
import { errorToast, successToast } from "@/utils/toaster";
import { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router";
import AuthLayout from "./AuthLayout";

export default function VerifyRegisterPage() {
  const navigate = useNavigate();
  const location = useLocation();

  const queryParams = new URLSearchParams(location.search);
  const email = queryParams.get("email");

  const [code, setCode] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [resendLoading, setResendLoading] = useState(false);
  const [resendCountdown, setResendCountdown] = useState(0);
  const [canResend, setCanResend] = useState(true);

  const mediguardApi = new MediguardApi(false, false, true);

  // Countdown effect
  useEffect(() => {
    let timer: NodeJS.Timeout;
    if (resendCountdown > 0) {
      timer = setTimeout(() => {
        setResendCountdown(resendCountdown - 1);
      }, 1000);
    } else if (resendCountdown === 0 && !canResend) {
      setCanResend(true);
    }
    return () => clearTimeout(timer);
  }, [resendCountdown, canResend]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!email) {
      setError("No email provided. Please sign up again.");
      return;
    }

    try {
      setLoading(true);
      setError(""); // Clear previous errors

      await mediguardApi.authApi.verifyEmail({ email, token: code });

      successToast("Email verified! You can now log in.");
      navigate("/login");
    } catch (err: any) {
      console.error(err);
      setError(err.detail?.message || "Invalid code.");
      errorToast(err.detail?.message || "Invalid code.");
    } finally {
      setLoading(false);
    }
  };

  const handleResend = async () => {
    if (!canResend || resendLoading) return;

    try {
      setResendLoading(true);
      await mediguardApi.authApi.resendVerificationEmail(email || "");
      successToast("Verification email sent. Please check your email.");

      // Start countdown (60 seconds)
      setResendCountdown(60);
      setCanResend(false);
      setError(""); // Clear any previous errors
    } catch (err: any) {
      console.error(err);
      setError(err.detail?.message || "Something went wrong.");
      errorToast(err.detail?.message || "Something went wrong.");
    } finally {
      setResendLoading(false);
    }
  };

  const handleBackToLogin = () => {
    navigate("/login");
  };

  return (
    <AuthLayout>
      <h2 className="text-3xl font-bold mb-6 text-center">
        Verify Your Account
      </h2>

      <p className="text-center text-sm text-gray-600 mb-5">
        Enter the 6-digit code we sent to your email address.
        {email && (
          <span className="block mt-1 text-blue-600 font-medium">{email}</span>
        )}
      </p>

      {error && (
        <p className="text-red-600 text-sm text-center mb-3">{error}</p>
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
            onChange={(e) => setCode(e.target.value.replace(/\D/g, ""))} // Only allow digits
            autoComplete="one-time-code"
          />
        </div>

        <button
          type="submit"
          disabled={loading || code.length !== 6}
          className={`w-full p-3 rounded-lg font-semibold transition flex items-center justify-center gap-2
            ${
              loading || code.length !== 6
                ? "bg-gray-300 cursor-not-allowed text-gray-500"
                : "bg-blue-600 hover:bg-blue-700 text-white"
            }`}
        >
          {loading && (
            <svg
              className="animate-spin h-5 w-5"
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
                d="m4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              ></path>
            </svg>
          )}
          {loading ? "Verifying..." : "Verify Account"}
        </button>
      </form>

      <div className="mt-5 space-y-3">
        {/* Resend Code Section */}
        <div className="text-sm text-center text-gray-600">
          Didn't receive code?{" "}
          <button
            onClick={handleResend}
            disabled={!canResend || resendLoading}
            className={`font-medium transition inline-flex items-center gap-1 ${
              canResend && !resendLoading
                ? "text-blue-600 hover:underline cursor-pointer"
                : "text-gray-400 cursor-not-allowed"
            }`}
          >
            {resendLoading && (
              <svg
                className="animate-spin h-3 w-3"
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
                  d="m4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                ></path>
              </svg>
            )}
            {resendLoading
              ? "Sending..."
              : canResend
              ? "Resend Code"
              : `Resend in ${resendCountdown}s`}
          </button>
        </div>

        {/* Back to Login Section */}
        <div className="text-sm text-center text-gray-600">
          Already have an account?{" "}
          <button
            onClick={handleBackToLogin}
            className="text-blue-600 hover:underline font-medium"
          >
            Back to Login
          </button>
        </div>
      </div>
    </AuthLayout>
  );
}

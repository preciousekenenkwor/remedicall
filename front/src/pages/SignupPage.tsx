/* eslint-disable @typescript-eslint/no-explicit-any */
import { MediguardApi } from "@/app/services";
import { errorToast } from "@/utils/toaster";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router";
import AuthLayout from "./AuthLayout";

// Password validation regex - customize as needed
const PASSWORD_REGEX =
  /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!.%*?&])[A-Za-z\d@$!.%*?&]{8,}$/;

// Full name validation - at least 2 words with letters only
const FULL_NAME_REGEX = /^[A-Za-z]+\s+[A-Za-z]+(\s+[A-Za-z]+)*$/;

interface PasswordValidation {
  minLength: boolean;
  hasUppercase: boolean;
  hasLowercase: boolean;
  hasNumber: boolean;
  hasSpecialChar: boolean;
}

export default function SignupPage() {
  const navigate = useNavigate(); 

  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [passwordValidation, setPasswordValidation] =
    useState<PasswordValidation>({
      minLength: false,
      hasUppercase: false,
      hasLowercase: false,
      hasNumber: false,
      hasSpecialChar: false,
    });
  const [showPasswordRequirements, setShowPasswordRequirements] =
    useState(false);

  const mediguardApi = new MediguardApi(false, false, true);

  // Validate password on change
  useEffect(() => {
    if (password) {
      setPasswordValidation({
        minLength: password.length >= 8,
        hasUppercase: /[A-Z]/.test(password),
        hasLowercase: /[a-z]/.test(password),
        hasNumber: /\d/.test(password),
        hasSpecialChar: /[@$!.%*?&]/.test(password),
      });
    } else {
      setPasswordValidation({
        minLength: false,
        hasUppercase: false,
        hasLowercase: false,
        hasNumber: false,
        hasSpecialChar: false,
      });
    }
  }, [password]);

  const isPasswordValid = () => {
    return PASSWORD_REGEX.test(password);
  };

  const isFullNameValid = () => {
    return FULL_NAME_REGEX.test(fullName.trim());
  };

  const isFormValid = () => {
    return (
      isFullNameValid() &&
      email.trim() &&
      isPasswordValid() &&
      password === confirmPassword
    );
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (!isPasswordValid()) {
      setError("Password does not meet requirements.");
      return;
    }

    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    try {
      setLoading(true);

      const response = await mediguardApi.authApi.signup({
        email: email,
        password: password,
        first_name: fullName.split(" ")[0],
        last_name: fullName.split(" ")[1],
        user_type: "patient",
      });

      console.log("User created:", response);
      navigate(`/verify-register?email=${encodeURIComponent(email)}`);
    } catch (err: any) {
      console.error(err, "--------------->>");
      errorToast(err.detail.message || "Something went wrong.");
      setError(err.detail.message || "Something went wrong.");
    } finally {
      setLoading(false);
    }
  };

  const ValidationCheck = ({
    isValid,
    text,
  }: {
    isValid: boolean;
    text: string;
  }) => (
    <div
      className={`flex items-center text-sm ${
        isValid ? "text-green-600" : "text-red-500"
      }`}
    >
      <span className="mr-2">{isValid ? "✓" : "✗"}</span>
      {text}
    </div>
  );

  return (
    <AuthLayout>
      <h2 className="text-3xl font-bold mb-6 text-center">Sign Up</h2>

      {error && (
        <p className="text-red-600 text-sm text-center mb-3">{error}</p>
      )}

      <form className="space-y-5" onSubmit={handleSubmit}>
        <div>
          <label className="block mb-1 font-medium">Full Name</label>
          <input
            type="text"
            className={`w-full border rounded-lg p-3 focus:outline-none focus:ring-2 transition-colors
              ${
                isFullNameValid() && fullName
                  ? "border-green-400 focus:ring-green-400"
                  : fullName && !isFullNameValid()
                  ? "border-red-400 focus:ring-red-400"
                  : "border-gray-300 focus:ring-blue-400"
              }`}
            placeholder="Enter your full name"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            required
          />
          {fullName && !isFullNameValid() && (
            <p className="text-red-500 text-sm mt-1">
              Please enter your first and last name
            </p>
          )}
          {fullName && isFullNameValid() && (
            <p className="text-green-600 text-sm mt-1">Valid name ✓</p>
          )}
        </div>

        <div>
          <label className="block mb-1 font-medium">Email</label>
          <input
            type="email"
            className="w-full border border-gray-300 rounded-lg p-3 focus:outline-none focus:ring-2 focus:ring-blue-400"
            placeholder="Enter your email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </div>

        <div>
          <label className="block mb-1 font-medium">Password</label>
          <input
            type="password"
            className={`w-full border rounded-lg p-3 focus:outline-none focus:ring-2 transition-colors
              ${
                isPasswordValid() && password
                  ? "border-green-400 focus:ring-green-400"
                  : password && !isPasswordValid()
                  ? "border-red-400 focus:ring-red-400"
                  : "border-gray-300 focus:ring-blue-400"
              }`}
            placeholder="Enter your password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            onFocus={() => setShowPasswordRequirements(true)}
            required
          />

          {/* Password Requirements - Auto-hide when all requirements are met */}
          {showPasswordRequirements && password && !isPasswordValid() && (
            <div className="mt-3 p-3 bg-gray-50 rounded-lg border">
              <h4 className="text-sm font-medium mb-2 text-gray-700">
                Password Requirements:
              </h4>
              <div className="space-y-1">
                <ValidationCheck
                  isValid={passwordValidation.minLength}
                  text="At least 8 characters"
                />
                <ValidationCheck
                  isValid={passwordValidation.hasUppercase}
                  text="One uppercase letter (A-Z)"
                />
                <ValidationCheck
                  isValid={passwordValidation.hasLowercase}
                  text="One lowercase letter (a-z)"
                />
                <ValidationCheck
                  isValid={passwordValidation.hasNumber}
                  text="One number (0-9)"
                />
                <ValidationCheck
                  isValid={passwordValidation.hasSpecialChar}
                  text="One special character (@$!.%*?&)"
                />
              </div>
            </div>
          )}

          {/* Show success message when password is valid */}
          {password && isPasswordValid() && (
            <p className="text-green-600 text-sm mt-1">Strong password ✓</p>
          )}
        </div>

        <div>
          <label className="block mb-1 font-medium">Confirm Password</label>
          <input
            type="password"
            className={`w-full border rounded-lg p-3 focus:outline-none focus:ring-2 transition-colors
              ${
                confirmPassword && password === confirmPassword
                  ? "border-green-400 focus:ring-green-400"
                  : confirmPassword && password !== confirmPassword
                  ? "border-red-400 focus:ring-red-400"
                  : "border-gray-300 focus:ring-blue-400"
              }`}
            placeholder="Confirm your password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            required
          />
          {confirmPassword && password !== confirmPassword && (
            <p className="text-red-500 text-sm mt-1">Passwords do not match</p>
          )}
          {confirmPassword && password === confirmPassword && (
            <p className="text-green-600 text-sm mt-1">Passwords match ✓</p>
          )}
        </div>

        <button
          type="submit"
          disabled={loading || !isFormValid()}
          className={`w-full p-3 rounded-lg font-semibold transition 
            ${
              loading || !isFormValid()
                ? "bg-gray-300 cursor-not-allowed text-gray-500"
                : "bg-blue-600 hover:bg-blue-700 text-white"
            }`}
        >
          {loading ? "Creating..." : "Create Account"}
        </button>

        {/* Form validation status */}
        {!isFormValid() &&
          (fullName || email || password || confirmPassword) && (
            <p className="text-sm text-gray-600 text-center">
              Please complete all fields with valid information to continue
            </p>
          )}
      </form>

      <div className="mt-5 text-sm text-center text-gray-600">
        Already have an account?{" "}
        <button
          onClick={() => navigate("/login")}
          className="text-blue-600 hover:underline"
        >
          Login here
        </button>
      </div>
    </AuthLayout>
  );
}

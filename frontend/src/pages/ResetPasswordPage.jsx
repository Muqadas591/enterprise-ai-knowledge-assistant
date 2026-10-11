import { useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { ArrowRight, CheckCircle2 } from "lucide-react";

import AuthLayout from "../components/auth/AuthLayout";
import PasswordInput from "../components/auth/PasswordInput";
import AuthMessage from "../components/auth/AuthMessage";
import { resetPassword } from "../api/auth";

function ResetPasswordPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  const token = searchParams.get("token");

  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] =
    useState("");

  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();

    setError("");

    if (!token) {
      setError("This password reset link is invalid.");
      return;
    }

    if (password.length < 8) {
      setError(
        "Password must contain at least 8 characters."
      );
      return;
    }

    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    setLoading(true);

    try {
      await resetPassword({ token, password });

      setSuccess(
        "Your password has been reset successfully."
      );

      setTimeout(() => {
        navigate("/login");
      }, 1800);
    } catch (err) {
      setError(
        err?.response?.data?.detail ||
          "This reset link is invalid or has expired."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthLayout>
      <div className="auth-heading">
        <div className="auth-icon-card success">
          <CheckCircle2 size={24} />
        </div>

        <h2>Create a new password</h2>

        <p>
          Choose a strong password that you haven't used
          previously.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="auth-form">
        <AuthMessage>{error}</AuthMessage>

        <AuthMessage type="success">
          {success}
        </AuthMessage>

        <PasswordInput
          label="New password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Enter new password"
          autoComplete="new-password"
        />

        <PasswordInput
          label="Confirm new password"
          value={confirmPassword}
          onChange={(e) =>
            setConfirmPassword(e.target.value)
          }
          placeholder="Confirm new password"
          autoComplete="new-password"
        />

        <button
          type="submit"
          className="auth-submit"
          disabled={loading}
        >
          {loading ? (
            <span className="button-loading">
              <span />
              Updating password...
            </span>
          ) : (
            <>
              Reset password
              <ArrowRight size={18} />
            </>
          )}
        </button>
      </form>

      <div className="auth-switch">
        <span>Remember your password?</span>

        <Link to="/login">
          Sign in
        </Link>
      </div>
    </AuthLayout>
  );
}

export default ResetPasswordPage;
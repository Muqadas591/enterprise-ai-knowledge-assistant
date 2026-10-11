import { useState } from "react";
import { ArrowLeft, Mail, ArrowRight } from "lucide-react";
import { Link } from "react-router-dom";

import AuthLayout from "../components/auth/AuthLayout";
import AuthMessage from "../components/auth/AuthMessage";
import { requestPasswordReset } from "../api/auth";

function ForgotPasswordPage() {
  const [email, setEmail] = useState("");

  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();

    setError("");
    setSuccess("");
    setLoading(true);

    try {
      const response = await requestPasswordReset({ email });

      setSuccess(
        response?.message ||
          "If an account exists for this email, a password reset link has been sent."
      );
    } catch (err) {
      setError(
        "Unable to process your request. Please try again."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthLayout>
      <div className="auth-heading">
        <Link to="/login" className="back-link">
          <ArrowLeft size={17} />
          Back to sign in
        </Link>

        <div className="auth-icon-card">
          <Mail size={24} />
        </div>

        <h2>Forgot your password?</h2>

        <p>
          Enter your account email. If an account exists, we&apos;ll send a reset link.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="auth-form">
        <AuthMessage type="error">
          {error}
        </AuthMessage>

        <AuthMessage type="success">
          {success}
        </AuthMessage>

        <div className="auth-field">
            <label htmlFor="forgot-email">Email address</label>

          <div className="input-with-icon">
            <Mail size={18} />

            <input
              id="forgot-email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@company.com"
              autoComplete="email"
              required
            />
          </div>
        </div>

        <button
          type="submit"
          className="auth-submit"
          disabled={loading}
        >
          {loading ? (
            <span className="button-loading">
              <span />
              Sending...
            </span>
          ) : (
            <>
              Send reset link
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

export default ForgotPasswordPage;
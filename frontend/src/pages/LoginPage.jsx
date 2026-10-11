import { useState } from "react";
import { ArrowRight, Mail, ShieldCheck } from "lucide-react";
import { Link as RouterLink, useLocation, useNavigate } from "react-router-dom";
import AuthLayout from "../components/auth/AuthLayout";
import PasswordInput from "../components/auth/PasswordInput";
import AuthMessage from "../components/auth/AuthMessage";

import { loginUser } from "../api/auth";
import { useAuth } from "../context/AuthContext";

export default function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const { login } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setLoading(true);

    try {
      const data = await loginUser({ email, password });
      login(data.access_token);
      navigate(location.state?.from?.pathname || "/");
    } catch (err) {
      setError(
        err?.response?.data?.detail ||
          "Unable to sign in. Please check your credentials.",
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <AuthLayout>
      <div className="auth-heading">
        <div className="mobile-auth-logo">Enterprise AI</div>
        <h2>Welcome back</h2>
        <p>Sign in to access your enterprise knowledge workspace.</p>
      </div>

      {location.state?.message && (
        <AuthMessage type="success">{location.state.message}</AuthMessage>
      )}

      <form onSubmit={handleSubmit} className="auth-form">
        <AuthMessage>{error}</AuthMessage>

        <div className="auth-field">
          <label htmlFor="email">Email address</label>
          <div className="input-with-icon">
            <Mail size={18} aria-hidden="true" />
            <input
              id="email"
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              placeholder="you@company.com"
              autoComplete="email"
              required
            />
          </div>
        </div>

        <PasswordInput
          label="Password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          autoComplete="current-password"
        />

        <div className="auth-options">
          <label className="remember-option">
            <input type="checkbox" />
            <span>Remember me</span>
          </label>
          <RouterLink to="/forgot-password">Forgot password?</RouterLink>
        </div>

        <button
          type="submit"
          className="auth-submit"
          disabled={loading}
        >
          {loading ? (
            <span className="button-loading">
              <span />
              Signing in...
            </span>
          ) : (
            <>
              Sign in
              <ArrowRight size={18} />
            </>
          )}
        </button>
      </form>

      <div className="auth-divider">
        <span />
        <p>OR</p>
        <span />
      </div>

      <div className="auth-switch">
        <span>Don&apos;t have an account?</span>
        <RouterLink to="/signup">Create an account</RouterLink>
      </div>

      <div className="auth-security">
        <ShieldCheck size={16} aria-hidden="true" />
        <span>Your connection is protected and secure.</span>
      </div>
    </AuthLayout>
  );
}
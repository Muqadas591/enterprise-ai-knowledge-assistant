import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { ArrowRight, Mail, User } from "lucide-react";

import AuthLayout from "../components/auth/AuthLayout";
import PasswordInput from "../components/auth/PasswordInput";
import AuthMessage from "../components/auth/AuthMessage";
import { registerUser } from "../api/auth";

function SignupPage() {
  const navigate = useNavigate();

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();

    setError("");

    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    if (password.length < 8) {
      setError(
        "Password must contain at least 8 characters."
      );
      return;
    }

    setLoading(true);

    try {
      await registerUser({
        email,
        password,
      });

      navigate("/login", {
        state: {
          message:
            "Account created successfully. You can now sign in.",
        },
      });
    } catch (err) {
      setError(
        err?.response?.data?.detail ||
          "Unable to create your account."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthLayout>
      <div className="auth-heading">
        <h2>Create your account</h2>

        <p>
          Start using your organization's intelligent
          knowledge assistant.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="auth-form">
        <AuthMessage>{error}</AuthMessage>

        <div className="auth-field">
          <label>Full name</label>

          <div className="input-with-icon">
            <User size={18} />

            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Your name"
              autoComplete="name"
              required
            />
          </div>
        </div>

        <div className="auth-field">
          <label>Email address</label>

          <div className="input-with-icon">
            <Mail size={18} />

            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@company.com"
              autoComplete="email"
              required
            />
          </div>
        </div>

        <PasswordInput
          label="Create password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Create a strong password"
          autoComplete="new-password"
        />

        <PasswordInput
          label="Confirm password"
          value={confirmPassword}
          onChange={(e) =>
            setConfirmPassword(e.target.value)
          }
          placeholder="Confirm your password"
          autoComplete="new-password"
        />

        <label className="terms-option">
          <input type="checkbox" required />
          <span>
            I agree to the platform's terms and privacy
            policy.
          </span>
        </label>

        <button
          type="submit"
          className="auth-submit"
          disabled={loading}
        >
          {loading ? (
            <span className="button-loading">
              <span />
              Creating account...
            </span>
          ) : (
            <>
              Create account
              <ArrowRight size={18} />
            </>
          )}
        </button>
      </form>

      <div className="auth-switch">
        <span>Already have an account?</span>

        <Link to="/login">
          Sign in
        </Link>
      </div>
    </AuthLayout>
  );
}

export default SignupPage;
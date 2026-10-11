import { Eye, EyeOff, LockKeyhole } from "lucide-react";
import { useState } from "react";

function PasswordInput({
  label = "Password",
  value,
  onChange,
  placeholder = "Enter your password",
  autoComplete = "current-password",
  required = true,
}) {
  const [showPassword, setShowPassword] = useState(false);

  return (
    <div className="auth-field">
      <label>{label}</label>

      <div className="password-wrapper">
        <LockKeyhole size={18} className="password-icon" />

        <input
          type={showPassword ? "text" : "password"}
          value={value}
          onChange={onChange}
          placeholder={placeholder}
          autoComplete={autoComplete}
          required={required}
        />

        <button
          type="button"
          className="password-toggle"
          onClick={() => setShowPassword((prev) => !prev)}
          aria-label={
            showPassword ? "Hide password" : "Show password"
          }
        >
          {showPassword ? (
            <EyeOff size={18} />
          ) : (
            <Eye size={18} />
          )}
        </button>
      </div>
    </div>
  );
}

export default PasswordInput;
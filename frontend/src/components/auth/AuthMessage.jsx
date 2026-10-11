import { AlertCircle, CheckCircle2 } from "lucide-react";

function AuthMessage({ type = "error", children }) {
  if (!children) return null;

  return (
    <div className={`auth-message ${type}`}>
      {type === "success" ? (
        <CheckCircle2 size={17} />
      ) : (
        <AlertCircle size={17} />
      )}

      <span>{children}</span>
    </div>
  );
}

export default AuthMessage;
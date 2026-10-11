import { ShieldCheck, Sparkles, Database, Search } from "lucide-react";

function AuthLayout({ children }) {
  return (
    <div className="auth-page">
      <div className="auth-background">
        <div className="auth-glow auth-glow-one" />
        <div className="auth-glow auth-glow-two" />
      </div>

      <div className="auth-container">
        <div className="auth-brand-panel">
          <div className="auth-brand">
            <div className="auth-logo">
              <Sparkles size={22} />
            </div>

            <div>
              <div className="auth-brand-name">
                Enterprise AI
              </div>

              <div className="auth-brand-subtitle">
                Knowledge Platform
              </div>
            </div>
          </div>

          <div className="auth-brand-content">
            <div className="auth-eyebrow">
              <span />
              INTELLIGENT KNOWLEDGE
            </div>

            <h1>
              Ask questions.
              <br />
              <span>Find answers.</span>
            </h1>

            <p>
              Securely search your organization's knowledge
              using AI-powered retrieval and grounded answers.
            </p>
          </div>

          <div className="auth-features">
            <div>
              <Database size={18} />
              <span>Enterprise knowledge</span>
            </div>

            <div>
              <Search size={18} />
              <span>Grounded RAG search</span>
            </div>

            <div>
              <ShieldCheck size={18} />
              <span>Secure access</span>
            </div>
          </div>

          <div className="auth-brand-footer">
            AI-powered knowledge, built for real business.
          </div>
        </div>

        <div className="auth-form-panel">
          <div className="auth-form-container">
            {children}
          </div>
        </div>
      </div>
    </div>
  );
}

export default AuthLayout;
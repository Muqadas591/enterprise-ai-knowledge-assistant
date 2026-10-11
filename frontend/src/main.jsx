import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";

import App from "./App";
import "./index.css";

import { AuthProvider } from "./context/AuthContext";
import { ConversationProvider } from "./context/ConversationContext";
import { DocumentProvider } from "./context/DocumentContext";

ReactDOM.createRoot(
  document.getElementById("root")
).render(
  <React.StrictMode>
    <BrowserRouter>
      <AuthProvider>
        <ConversationProvider>
          <DocumentProvider>
            <App />
          </DocumentProvider>
        </ConversationProvider>
      </AuthProvider>
    </BrowserRouter>
  </React.StrictMode>
);
import { Navigate, Outlet } from "react-router-dom";

export default function ProtectedRoute() {
  const token = localStorage.getItem("access_token");

  // If no token exists, send user to the login page
  if (!token) {
    return <Navigate to="/login" replace />;
  }

  // If token exists, render the child page/component
  return <Outlet />;
}
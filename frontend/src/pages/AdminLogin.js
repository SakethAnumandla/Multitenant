import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { adminAPI, setAuthToken, setUser } from "../services/api";

function AdminLogin() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    email: "",
    password: "",
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
    setError("");
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      const response = await adminAPI.login(formData);

      // Save token and user data
      setAuthToken(response.data.token);
      const userData = {
        ...response.data.admin,
        user_type: "admin",
      };
      setUser(userData);

      // Redirect to dashboard
      navigate("/admin/dashboard");
    } catch (err) {
      setError(err.response?.data?.error || "Login failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="form-container">
      <h2 className="form-title">🔐 Admin Login</h2>

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="email">Email Address</label>
          <input
            type="email"
            id="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            placeholder="admin@multitenant.com"
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="password">Password</label>
          <input
            type="password"
            id="password"
            name="password"
            value={formData.password}
            onChange={handleChange}
            placeholder="Enter your password"
            required
          />
        </div>

        {error && <div className="form-error">{error}</div>}

        <button
          type="submit"
          className="btn btn-primary"
          style={{ width: "100%" }}
          disabled={loading}
        >
          {loading ? "Logging in..." : "Login"}
        </button>
      </form>

      <div
        style={{
          marginTop: "1rem",
          textAlign: "center",
          fontSize: "0.9rem",
          color: "#666",
        }}
      >
        <p>Default Credentials:</p>
        <p>
          <strong>Email:</strong> admin@multitenant.com
        </p>
        <p>
          <strong>Password:</strong> Admin@12345
        </p>
      </div>
    </div>
  );
}

export default AdminLogin;

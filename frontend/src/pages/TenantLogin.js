import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { tenantAPI, setAuthToken, setUser } from "../services/api";

function TenantLogin() {
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
      const response = await tenantAPI.login(formData);

      // Save token and user data
      setAuthToken(response.data.token);
      const userData = {
        ...response.data.tenant,
        user_type: "tenant",
        name: response.data.tenant.admin_name,
      };
      setUser(userData);

      // Redirect to dashboard
      navigate("/tenant/dashboard");
    } catch (err) {
      setError(err.response?.data?.error || "Login failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="form-container">
      <h2 className="form-title">🏢 Tenant Login</h2>

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="email">Admin Email Address</label>
          <input
            type="email"
            id="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            placeholder="your-email@company.com"
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
        <p>Tenant admin credentials are created by the system administrator</p>
      </div>
    </div>
  );
}

export default TenantLogin;

import React, { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { userAPI, setAuthToken, setUser } from "../services/api";

function UserLogin() {
  const navigate = useNavigate();
  const { slug } = useParams();
  const [formData, setFormData] = useState({
    email: "",
    password: "",
    tenant_id: "",
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
      let response;

      // Login via tenant slug if provided in URL
      if (slug) {
        response = await userAPI.loginBySlug(slug, {
          email: formData.email,
          password: formData.password,
        });
      } else {
        response = await userAPI.login(formData);
      }

      // Check if password reset is required
      if (response.data.password_reset_required) {
        alert("Password reset required. Please set a new password.");
        // TODO: Redirect to password reset page
        return;
      }

      // Save token and user data
      setAuthToken(response.data.token);
      const userData = {
        ...response.data.user,
        user_type: "user",
      };
      setUser(userData);

      // Redirect to dashboard
      navigate("/user/dashboard");
    } catch (err) {
      setError(err.response?.data?.error || "Login failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="form-container">
      <h2 className="form-title">👥 User Login</h2>

      {slug && (
        <div
          style={{
            textAlign: "center",
            marginBottom: "1rem",
            color: "#667eea",
          }}
        >
          <p>
            Logging in to: <strong>{slug}</strong>
          </p>
        </div>
      )}

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="email">Email Address</label>
          <input
            type="email"
            id="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            placeholder="your-email@example.com"
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

        {!slug && (
          <div className="form-group">
            <label htmlFor="tenant_id">Tenant ID (Optional)</label>
            <input
              type="number"
              id="tenant_id"
              name="tenant_id"
              value={formData.tenant_id}
              onChange={handleChange}
              placeholder="Leave empty if unsure"
            />
          </div>
        )}

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
        <p>Don't have an account? Contact your organization administrator</p>
      </div>
    </div>
  );
}

export default UserLogin;


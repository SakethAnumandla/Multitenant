import React, { useState, useEffect } from "react";
import { tenantAPI } from "../services/api";

function TenantDashboard() {
  const [stats, setStats] = useState(null);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showCreateForm, setShowCreateForm] = useState(false);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [dashboardRes, usersRes] = await Promise.all([
        tenantAPI.getDashboard(),
        tenantAPI.getUsers(1, 10),
      ]);

      setStats(dashboardRes.data.stats);
      setUsers(usersRes.data.users);
    } catch (err) {
      setError("Failed to load dashboard data");
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteUser = async (userId, userName) => {
    if (
      window.confirm(
        `Are you sure you want to delete user "${userName}"?`
      )
    ) {
      try {
        await tenantAPI.deleteUser(userId);
        alert("User deleted successfully");
        fetchDashboardData();
      } catch (err) {
        alert(err.response?.data?.error || "Failed to delete user");
      }
    }
  };

  if (loading) {
    return (
      <div className="loading">
        <div className="spinner"></div>
        <p>Loading dashboard...</p>
      </div>
    );
  }

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>🏢 Tenant Dashboard</h1>
        <p>Manage your users and employees</p>
      </div>

      {error && <div className="form-error">{error}</div>}

      {/* Statistics Cards */}
      {stats && (
        <div className="dashboard-stats">
          <div className="stat-card">
            <h3>Total Users</h3>
            <div className="stat-value">{stats.total_users}</div>
          </div>
          <div className="stat-card">
            <h3>Active Users</h3>
            <div className="stat-value">{stats.active_users}</div>
          </div>
          <div className="stat-card">
            <h3>Employees</h3>
            <div className="stat-value">{stats.employees}</div>
          </div>
          <div className="stat-card">
            <h3>Regular Users</h3>
            <div className="stat-value">{stats.regular_users}</div>
          </div>
        </div>
      )}

      {/* Users List */}
      <div className="dashboard-content">
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            marginBottom: "1.5rem",
          }}
        >
          <h2>User Management</h2>
          <button
            className="btn btn-primary"
            onClick={() => setShowCreateForm(!showCreateForm)}
          >
            {showCreateForm ? "Cancel" : "+ Add User"}
          </button>
        </div>

        {showCreateForm && (
          <CreateUserForm
            onSuccess={fetchDashboardData}
            onCancel={() => setShowCreateForm(false)}
          />
        )}

        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Email</th>
                <th>Phone</th>
                <th>Role</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {users.length === 0 ? (
                <tr>
                  <td
                    colSpan="7"
                    style={{ textAlign: "center", padding: "2rem" }}
                  >
                    No users found. Add your first user!
                  </td>
                </tr>
              ) : (
                users.map((user) => (
                  <tr key={user.id}>
                    <td>{user.id}</td>
                    <td>{user.name}</td>
                    <td>{user.email}</td>
                    <td>{user.phone || "N/A"}</td>
                    <td>
                      <span
                        style={{
                          background:
                            user.role === "user"
                              ? "#48dbfb"
                              : "#ffa502",
                          color: "white",
                          padding: "0.25rem 0.5rem",
                          borderRadius: "3px",
                          fontSize: "0.85rem",
                        }}
                      >
                        {user.role}
                      </span>
                    </td>
                    <td>
                      <span
                        style={{
                          color: user.is_active ? "#2ed573" : "#ff4757",
                          fontWeight: "bold",
                        }}
                      >
                        {user.is_active ? "✓ Active" : "✗ Inactive"}
                      </span>
                    </td>
                    <td className="actions">
                      <button
                        className="action-btn action-btn-delete"
                        onClick={() =>
                          handleDeleteUser(user.id, user.name)
                        }
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

// Create User Form Component
function CreateUserForm({ onSuccess, onCancel }) {
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    phone: "",
    password: "",
    role: "user",
    access_level: "basic",
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
      await tenantAPI.createUser(formData);
      alert("User created successfully!");
      onSuccess();
      onCancel();
    } catch (err) {
      setError(err.response?.data?.error || "Failed to create user");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        background: "#f8f9fa",
        padding: "1.5rem",
        borderRadius: "8px",
        marginBottom: "2rem",
      }}
    >
      <h3 style={{ marginBottom: "1rem" }}>Add New User</h3>
      <form onSubmit={handleSubmit}>
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "1fr 1fr",
            gap: "1rem",
          }}
        >
          <div className="form-group">
            <label>Name *</label>
            <input
              type="text"
              name="name"
              value={formData.name}
              onChange={handleChange}
              required
            />
          </div>
          <div className="form-group">
            <label>Email *</label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              required
            />
          </div>
          <div className="form-group">
            <label>Phone</label>
            <input
              type="tel"
              name="phone"
              value={formData.phone}
              onChange={handleChange}
            />
          </div>
          <div className="form-group">
            <label>Role *</label>
            <select
              name="role"
              value={formData.role}
              onChange={handleChange}
              required
            >
              <option value="user">User</option>
              <option value="employee">Employee</option>
              <option value="manager">Manager</option>
              <option value="sales_rep">Sales Rep</option>
            </select>
          </div>
          <div className="form-group">
            <label>
              Password{" "}
              {formData.role === "user"
                ? "*"
                : "(Auto-generated for employees)"}
            </label>
            <input
              type="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              required={formData.role === "user"}
              disabled={formData.role !== "user"}
              placeholder={
                formData.role !== "user"
                  ? "Auto-generated"
                  : "Enter password"
              }
            />
          </div>
          <div className="form-group">
            <label>Access Level *</label>
            <select
              name="access_level"
              value={formData.access_level}
              onChange={handleChange}
              required
            >
              <option value="basic">Basic</option>
              <option value="premium">Premium</option>
              <option value="admin">Admin</option>
            </select>
          </div>
        </div>

        {error && (
          <div className="form-error" style={{ marginTop: "1rem" }}>
            {error}
          </div>
        )}

        <div style={{ display: "flex", gap: "1rem", marginTop: "1rem" }}>
          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? "Creating..." : "Create User"}
          </button>
          <button
            type="button"
            className="btn btn-secondary"
            onClick={onCancel}
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
}

export default TenantDashboard;

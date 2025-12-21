import React, { useState, useEffect } from "react";
import { adminAPI } from "../services/api";

function AdminDashboard() {
  const [stats, setStats] = useState(null);
  const [tenants, setTenants] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showCreateForm, setShowCreateForm] = useState(false);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [dashboardRes, tenantsRes] = await Promise.all([
        adminAPI.getDashboard(),
        adminAPI.getTenants(1, 10),
      ]);

      setStats(dashboardRes.data.stats);
      setTenants(tenantsRes.data.tenants);
    } catch (err) {
      setError("Failed to load dashboard data");
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteTenant = async (tenantId, tenantName) => {
    if (
      window.confirm(`Are you sure you want to delete tenant "${tenantName}"?`)
    ) {
      try {
        await adminAPI.deleteTenant(tenantId);
        alert("Tenant deleted successfully");
        fetchDashboardData();
      } catch (err) {
        alert(err.response?.data?.error || "Failed to delete tenant");
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
        <h1>🔐 Admin Dashboard</h1>
        <p>Manage tenants and monitor system activity</p>
      </div>

      {error && <div className="form-error">{error}</div>}

      {/* Statistics Cards */}
      {stats && (
        <div className="dashboard-stats">
          <div className="stat-card">
            <h3>Total Tenants</h3>
            <div className="stat-value">{stats.total_tenants}</div>
          </div>
          <div className="stat-card">
            <h3>Active Tenants</h3>
            <div className="stat-value">{stats.active_tenants}</div>
          </div>
          <div className="stat-card">
            <h3>Inactive Tenants</h3>
            <div className="stat-value">{stats.inactive_tenants}</div>
          </div>
          <div className="stat-card">
            <h3>Total Users</h3>
            <div className="stat-value">{stats.total_users}</div>
          </div>
        </div>
      )}

      {/* Tenants List */}
      <div className="dashboard-content">
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            marginBottom: "1.5rem",
          }}
        >
          <h2>Tenants Management</h2>
          <button
            className="btn btn-primary"
            onClick={() => setShowCreateForm(!showCreateForm)}
          >
            {showCreateForm ? "Cancel" : "+ Create Tenant"}
          </button>
        </div>

        {showCreateForm && (
          <CreateTenantForm
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
                <th>Slug</th>
                <th>Email</th>
                <th>Admin Email</th>
                <th>Status</th>
                <th>Subscription</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {tenants.length === 0 ? (
                <tr>
                  <td
                    colSpan="8"
                    style={{ textAlign: "center", padding: "2rem" }}
                  >
                    No tenants found. Create your first tenant!
                  </td>
                </tr>
              ) : (
                tenants.map((tenant) => (
                  <tr key={tenant.id}>
                    <td>{tenant.id}</td>
                    <td>{tenant.name}</td>
                    <td>
                      <code
                        style={{
                          background: "#f1f2f6",
                          padding: "0.2rem 0.5rem",
                          borderRadius: "3px",
                        }}
                      >
                        /{tenant.slug}
                      </code>
                    </td>
                    <td>{tenant.email}</td>
                    <td>{tenant.admin_email}</td>
                    <td>
                      <span
                        style={{
                          color: tenant.is_active ? "#2ed573" : "#ff4757",
                          fontWeight: "bold",
                        }}
                      >
                        {tenant.is_active ? "✓ Active" : "✗ Inactive"}
                      </span>
                    </td>
                    <td>{tenant.subscription_status}</td>
                    <td className="actions">
                      <button
                        className="action-btn action-btn-delete"
                        onClick={() =>
                          handleDeleteTenant(tenant.id, tenant.name)
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

// Create Tenant Form Component
function CreateTenantForm({ onSuccess, onCancel }) {
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    phone: "",
    admin_name: "",
    admin_email: "",
    admin_password: "",
    metadata: {
      gst: "",
      pan: "",
      address: "",
    },
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;

    if (name.startsWith("metadata.")) {
      const metadataKey = name.split(".")[1];
      setFormData({
        ...formData,
        metadata: {
          ...formData.metadata,
          [metadataKey]: value,
        },
      });
    } else {
      setFormData({
        ...formData,
        [name]: value,
      });
    }
    setError("");
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      await adminAPI.createTenant(formData);
      alert("Tenant created successfully!");
      onSuccess();
      onCancel();
    } catch (err) {
      setError(err.response?.data?.error || "Failed to create tenant");
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
      <h3 style={{ marginBottom: "1rem" }}>Create New Tenant</h3>
      <form onSubmit={handleSubmit}>
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "1fr 1fr",
            gap: "1rem",
          }}
        >
          <div className="form-group">
            <label>Business Name *</label>
            <input
              type="text"
              name="name"
              value={formData.name}
              onChange={handleChange}
              required
            />
          </div>
          <div className="form-group">
            <label>Business Email *</label>
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
            <label>Admin Name *</label>
            <input
              type="text"
              name="admin_name"
              value={formData.admin_name}
              onChange={handleChange}
              required
            />
          </div>
          <div className="form-group">
            <label>Admin Email *</label>
            <input
              type="email"
              name="admin_email"
              value={formData.admin_email}
              onChange={handleChange}
              required
            />
          </div>
          <div className="form-group">
            <label>Admin Password *</label>
            <input
              type="password"
              name="admin_password"
              value={formData.admin_password}
              onChange={handleChange}
              required
            />
          </div>
          <div className="form-group">
            <label>GST Number</label>
            <input
              type="text"
              name="metadata.gst"
              value={formData.metadata.gst}
              onChange={handleChange}
            />
          </div>
          <div className="form-group">
            <label>PAN Number</label>
            <input
              type="text"
              name="metadata.pan"
              value={formData.metadata.pan}
              onChange={handleChange}
            />
          </div>
        </div>

        {error && (
          <div className="form-error" style={{ marginTop: "1rem" }}>
            {error}
          </div>
        )}

        <div style={{ display: "flex", gap: "1rem", marginTop: "1rem" }}>
          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? "Creating..." : "Create Tenant"}
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

export default AdminDashboard;

import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { userAPI, testAPI, getUser } from "../services/api";

function UserDashboard() {
  const navigate = useNavigate();
  const [profile, setProfile] = useState(null);
  const [tests, setTests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [editMode, setEditMode] = useState(false);

  useEffect(() => {
    fetchProfile();
    fetchTests();
  }, []);

  const fetchTests = async () => {
    try {
      const response = await testAPI.getTests();
      setTests(response.data.tests || []);
    } catch (err) {
      console.error("Failed to load tests:", err);
    }
  };

  const fetchProfile = async () => {
    try {
      const response = await userAPI.getProfile();
      setProfile(response.data.user);
    } catch (err) {
      setError("Failed to load profile");
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="loading">
        <div className="spinner"></div>
        <p>Loading profile...</p>
      </div>
    );
  }

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>👥 User Dashboard</h1>
        <p>Welcome back, {profile?.name}!</p>
      </div>

      {error && <div className="form-error">{error}</div>}

      {/* Profile Information */}
      <div className="dashboard-content">
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            marginBottom: "1.5rem",
          }}
        >
          <h2>Your Profile</h2>
          <button
            className="btn btn-primary"
            onClick={() => setEditMode(!editMode)}
          >
            {editMode ? "Cancel" : "Edit Profile"}
          </button>
        </div>

        {editMode ? (
          <EditProfileForm
            profile={profile}
            onSuccess={fetchProfile}
            onCancel={() => setEditMode(false)}
          />
        ) : (
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "1fr 1fr",
              gap: "1.5rem",
            }}
          >
            <div>
              <h3 style={{ marginBottom: "0.5rem", color: "#667eea" }}>
                Personal Information
              </h3>
              <div
                style={{
                  background: "#f8f9fa",
                  padding: "1rem",
                  borderRadius: "8px",
                }}
              >
                <p>
                  <strong>Name:</strong> {profile?.name}
                </p>
                <p>
                  <strong>Email:</strong> {profile?.email}
                </p>
                <p>
                  <strong>Phone:</strong> {profile?.phone || "Not provided"}
                </p>
                <p>
                  <strong>Role:</strong> {profile?.role}
                </p>
                <p>
                  <strong>Access Level:</strong> {profile?.access_level}
                </p>
              </div>
            </div>

            <div>
              <h3 style={{ marginBottom: "0.5rem", color: "#667eea" }}>
                Account Status
              </h3>
              <div
                style={{
                  background: "#f8f9fa",
                  padding: "1rem",
                  borderRadius: "8px",
                }}
              >
                <p>
                  <strong>Status:</strong>
                  <span
                    style={{
                      color: profile?.is_active ? "#2ed573" : "#ff4757",
                      fontWeight: "bold",
                      marginLeft: "0.5rem",
                    }}
                  >
                    {profile?.is_active ? "✓ Active" : "✗ Inactive"}
                  </span>
                </p>
                <p>
                  <strong>Verified:</strong>
                  <span
                    style={{
                      color: profile?.is_verified ? "#2ed573" : "#ffa502",
                      fontWeight: "bold",
                      marginLeft: "0.5rem",
                    }}
                  >
                    {profile?.is_verified ? "✓ Verified" : "⚠ Not Verified"}
                  </span>
                </p>
                <p>
                  <strong>Last Login:</strong>{" "}
                  {profile?.last_login
                    ? new Date(profile.last_login).toLocaleString()
                    : "N/A"}
                </p>
                <p>
                  <strong>Member Since:</strong>{" "}
                  {new Date(profile?.created_at).toLocaleDateString()}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Available Tests */}
        <div style={{ marginTop: "2rem" }}>
          <h3 style={{ marginBottom: "1rem", color: "#667eea" }}>
            Available Tests
          </h3>
          {tests.length === 0 ? (
            <div
              style={{
                background: "#f8f9fa",
                padding: "2rem",
                borderRadius: "8px",
                textAlign: "center",
              }}
            >
              <p style={{ color: "#999" }}>No tests available at the moment.</p>
            </div>
          ) : (
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fill, minmax(300px, 1fr))",
                gap: "1rem",
              }}
            >
              {tests.map((test) => (
                <div
                  key={test.id}
                  style={{
                    background: "#f8f9fa",
                    padding: "1.5rem",
                    borderRadius: "8px",
                    border: "1px solid #e0e0e0",
                  }}
                >
                  <h4 style={{ marginBottom: "0.5rem", color: "#333" }}>
                    {test.title}
                  </h4>
                  {test.description && (
                    <p style={{ fontSize: "0.9rem", color: "#666", marginBottom: "1rem" }}>
                      {test.description}
                    </p>
                  )}
                  <p style={{ fontSize: "0.85rem", color: "#999", marginBottom: "1rem" }}>
                    {test.questions_count || 0} questions
                  </p>
                  <button
                    className="btn btn-primary"
                    onClick={() => navigate(`/test/${test.id}`)}
                    style={{ width: "100%" }}
                  >
                    Start Test
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// Edit Profile Form Component
function EditProfileForm({ profile, onSuccess, onCancel }) {
  const [formData, setFormData] = useState({
    name: profile?.name || "",
    phone: profile?.phone || "",
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
      await userAPI.updateProfile(formData);
      alert("Profile updated successfully!");
      onSuccess();
      onCancel();
    } catch (err) {
      setError(err.response?.data?.error || "Failed to update profile");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{ background: "#f8f9fa", padding: "1.5rem", borderRadius: "8px" }}
    >
      <h3 style={{ marginBottom: "1rem" }}>Edit Profile</h3>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Name</label>
          <input
            type="text"
            name="name"
            value={formData.name}
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

        {error && <div className="form-error">{error}</div>}

        <div style={{ display: "flex", gap: "1rem", marginTop: "1rem" }}>
          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? "Updating..." : "Update Profile"}
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

export default UserDashboard;


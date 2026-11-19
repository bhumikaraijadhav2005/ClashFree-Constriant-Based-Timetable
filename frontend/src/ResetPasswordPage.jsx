// frontend/src/ResetPasswordPage.jsx
// Dedicated Self-Service Password Reset Page
// Displayed when the user clicks their institutional email password reset link.

import React, { useState } from "react";
import * as api from "./api";

export default function ResetPasswordPage({ token, onComplete }) {
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMessage("");

    if (!newPassword || newPassword.length < 6) {
      setErrorMessage("New password must be at least 6 characters long.");
      return;
    }

    if (newPassword !== confirmPassword) {
      setErrorMessage("Passwords do not match. Please ensure both fields are identical.");
      return;
    }

    setLoading(true);
    try {
      const res = await api.resetPasswordWithToken(token, newPassword);
      if (res.success) {
        setSuccess(true);
      } else {
        setErrorMessage(res.error || "Failed to reset password. Link may be expired.");
      }
    } catch {
      setErrorMessage("Network error connecting to ClashFree server. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-root">
      {/* Background Lighting & Glows */}
      <div className="login-glow login-glow-1" />
      <div className="login-glow login-glow-2" />

      <div className="login-container" style={{ maxWidth: "480px", margin: "auto" }}>
        <div className="login-card" style={{ width: "100%" }}>
          <div className="login-card-header">
            <div className="login-avatar-icon">
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <rect width="18" height="11" x="3" y="11" rx="2" ry="2" />
                <path d="M7 11V7a5 5 0 0 1 10 0v4" />
              </svg>
            </div>
            <h2 className="login-card-title">Set New Password</h2>
            <p className="login-card-subtitle">
              Choose a strong, secure password for your ClashFree account.
            </p>
          </div>

          {/* Error Message */}
          {errorMessage && (
            <div className="login-alert login-alert-error" role="alert">
              <span>⚠️</span>
              <span>{errorMessage}</span>
            </div>
          )}

          {/* Success State */}
          {success ? (
            <div style={{ textAlign: "center", padding: "16px 0" }}>
              <div
                style={{
                  width: "56px",
                  height: "56px",
                  borderRadius: "50%",
                  background: "rgba(16, 185, 129, 0.2)",
                  border: "2px solid #10b981",
                  color: "#10b981",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontSize: "26px",
                  margin: "0 auto 16px",
                }}
              >
                ✓
              </div>
              <h3 style={{ margin: "0 0 8px 0", color: "#f8fafc", fontSize: "1.2rem", fontWeight: 700 }}>
                Password Updated!
              </h3>
              <p style={{ margin: "0 0 24px 0", color: "#94a3b8", fontSize: "0.9rem" }}>
                Your account password has been successfully reset. You can now sign in using your new credentials.
              </p>
              <button
                type="button"
                className="login-submit-btn"
                onClick={onComplete}
              >
                Proceed to Sign In &rarr;
              </button>
            </div>
          ) : (
            /* Reset Password Form */
            <form onSubmit={handleSubmit} className="login-form">
              {/* New Password */}
              <div className="login-field-group">
                <label className="login-input-label">New Password</label>
                <div className="login-input-wrapper">
                  <span className="login-input-icon">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <rect width="18" height="11" x="3" y="11" rx="2" ry="2" />
                      <path d="M7 11V7a5 5 0 0 1 10 0v4" />
                    </svg>
                  </span>
                  <input
                    type={showPassword ? "text" : "password"}
                    placeholder="Enter at least 6 characters"
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    required
                    autoComplete="new-password"
                    className="login-input"
                  />
                  <button
                    type="button"
                    className="login-toggle-password"
                    onClick={() => setShowPassword(!showPassword)}
                    tabIndex={-1}
                    aria-label={showPassword ? "Hide password" : "Show password"}
                  >
                    {showPassword ? (
                      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="m15 18-.722-3.25" />
                        <path d="M2 8a10.645 10.645 0 0 0 20 0" />
                        <path d="m20 15-1.726-2.05" />
                        <path d="m4 15 1.726-2.05" />
                        <path d="m9 18 .722-3.25" />
                      </svg>
                    ) : (
                      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z" />
                        <circle cx="12" cy="12" r="3" />
                      </svg>
                    )}
                  </button>
                </div>
              </div>

              {/* Confirm Password */}
              <div className="login-field-group">
                <label className="login-input-label">Confirm New Password</label>
                <div className="login-input-wrapper">
                  <span className="login-input-icon">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <rect width="18" height="11" x="3" y="11" rx="2" ry="2" />
                      <path d="M7 11V7a5 5 0 0 1 10 0v4" />
                    </svg>
                  </span>
                  <input
                    type={showPassword ? "text" : "password"}
                    placeholder="Re-enter your new password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    required
                    autoComplete="new-password"
                    className="login-input"
                  />
                </div>
              </div>

              {/* Submit Button */}
              <button
                type="submit"
                className="login-submit-btn"
                disabled={loading}
                style={{ marginTop: "10px" }}
              >
                {loading ? (
                  <span style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: "8px" }}>
                    <span className="spinner-circle" />
                    Updating Password...
                  </span>
                ) : (
                  <span>Update Password &rarr;</span>
                )}
              </button>

              <button
                type="button"
                className="login-back-btn"
                onClick={onComplete}
                style={{ marginTop: "14px" }}
              >
                &larr; Cancel and return to Sign In
              </button>
            </form>
          )}

          {/* Footer */}
          <div className="login-footer-trust" style={{ marginTop: "24px" }}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10" />
            </svg>
            <span>End-to-End Encrypted &bull; Institutional Authentication</span>
          </div>
        </div>
      </div>
    </div>
  );
}

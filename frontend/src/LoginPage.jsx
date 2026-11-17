// frontend/src/LoginPage.jsx
// ClashFree Enterprise Sign-In Screen
// Two-column split layout, dark violet SaaS theme, responsive mobile stack,
// Supabase Auth integration, session management, and role testing presets.

import React, { useState } from "react";
import * as api from "./api";

const DEMO_ACCOUNTS = [
  {
    role: "SUPER_ADMIN",
    label: "Super Admin",
    email: "superadmin@clashfree.edu",
    designation: "Platform Architect",
    scope: "Platform-wide (All Colleges & Depts)"
  },
  {
    role: "INSTITUTIONAL_VIEWER",
    label: "Principal (Institutional Viewer)",
    email: "principal@clashfree.edu",
    designation: "Principal & Campus Director",
    scope: "College-wide Read-Only"
  },
  {
    role: "HOD",
    label: "HOD (CSE)",
    email: "hod.cse@clashfree.edu",
    designation: "Professor & HOD CSE",
    scope: "CSE Department Full Control"
  },
  {
    role: "TIMETABLE_CREATOR",
    label: "Timetable Creator (CSE)",
    email: "creator.cse@clashfree.edu",
    designation: "Asst. Professor & Coordinator",
    scope: "CSE Scheduling & Generation"
  },
  {
    role: "FACULTY",
    label: "Faculty (CSE)",
    email: "faculty.cse@clashfree.edu",
    designation: "Assistant Professor",
    scope: "CSE Department Timetable Viewer"
  }
];

export default function LoginPage({ onLoginSuccess }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(true);
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [infoMessage, setInfoMessage] = useState("");
  const [showForgotPassword, setShowForgotPassword] = useState(false);
  const [resetEmail, setResetEmail] = useState("");
  const [resetLoading, setResetLoading] = useState(false);
  const [showDemoDrawer, setShowDemoDrawer] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMessage("");
    setInfoMessage("");

    if (!email.trim()) {
      setErrorMessage("Please enter your email address.");
      return;
    }
    if (!password) {
      setErrorMessage("Please enter your password.");
      return;
    }

    setLoading(true);
    try {
      const res = await api.login(email.trim(), password, rememberMe);
      if (res.ok && res.success) {
        if (onLoginSuccess) {
          onLoginSuccess(res.user);
        }
      } else {
        setErrorMessage(res.error || "Invalid email or password. Please try again.");
      }
    } catch (err) {
      setErrorMessage("Could not connect to the ClashFree server. Please verify the backend is running.");
    } finally {
      setLoading(false);
    }
  };

  const handleForgotPassword = async (e) => {
    e.preventDefault();
    if (!resetEmail.trim()) {
      setErrorMessage("Please enter your email to receive reset instructions.");
      return;
    }
    setResetLoading(true);
    try {
      const res = await api.requestPasswordReset(resetEmail.trim());
      setInfoMessage(res.message || "Password reset instructions dispatched. Check your inbox.");
      setShowForgotPassword(false);
      setResetEmail("");
    } catch {
      setErrorMessage("Could not submit password reset request. Please try again.");
    } finally {
      setResetLoading(false);
    }
  };

  const selectDemoAccount = (acc) => {
    setEmail(acc.email);
    setPassword("ClashFree@2026");
    setErrorMessage("");
    setInfoMessage(`Loaded test account for ${acc.label}`);
  };

  return (
    <div className="login-root">
      {/* Top right floating institutional badge */}
      <div className="login-top-badge">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ color: "#a855f7" }}>
          <path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
          <polyline points="9 22 9 12 15 12 15 22" />
        </svg>
        <span>ClashFree</span>
      </div>

      <div className="login-container">
        {/* Left Section: Branding & Highlights */}
        <div className="login-left">
          {/* Logo Brand */}
          <div className="login-brand-header">
            <div className="login-brand-icon">
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#a855f7" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                <rect width="18" height="18" x="3" y="4" rx="2" ry="2" />
                <line x1="16" x2="16" y1="2" y2="6" />
                <line x1="8" x2="8" y1="2" y2="6" />
                <line x1="3" x2="21" y1="10" y2="10" />
                <path d="M12 14v4" />
                <path d="M12 14h2" />
              </svg>
            </div>
            <div>
              <div className="login-brand-title">
                Clash<span className="login-brand-accent">Free</span>
              </div>
              <div className="login-brand-subtitle">Constraint Based Timetable Scheduler</div>
            </div>
          </div>

          {/* Headline */}
          <div className="login-headline">
            <h1>
              Smart Scheduling.
              <span className="login-headline-gradient"> Clash Free Tomorrow.</span>
            </h1>
            <p className="login-headline-desc">
              Generate efficient, conflict-free timetables with ease — for every department, every semester.
            </p>
          </div>

          {/* 3 Feature Cards */}
          <div className="login-features">
            <div className="login-feature-card">
              <div className="feature-icon-box">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor" style={{ color: "#a855f7" }}>
                  <path d="M13 2 3 14h9l-1 8 10-12h-9l1-8z" />
                </svg>
              </div>
              <div>
                <div className="feature-title">Automated Scheduling</div>
                <div className="feature-desc">Powerful CSP-based engine</div>
              </div>
            </div>

            <div className="login-feature-card">
              <div className="feature-icon-box">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#a855f7" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
                  <path d="m9 12 2 2 4-4" />
                </svg>
              </div>
              <div>
                <div className="feature-title">Conflict Free</div>
                <div className="feature-desc">Smart constraint handling</div>
              </div>
            </div>

            <div className="login-feature-card">
              <div className="feature-icon-box">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#a855f7" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                  <line x1="18" x2="18" y1="20" y2="10" />
                  <line x1="12" x2="12" y1="20" y2="4" />
                  <line x1="6" x2="6" y1="20" y2="14" />
                </svg>
              </div>
              <div>
                <div className="feature-title">Complete Visibility</div>
                <div className="feature-desc">From master timetable to workload</div>
              </div>
            </div>
          </div>

          {/* Stylized Collegiate Vector Illustration */}
          <div className="login-campus-illustration" aria-hidden="true">
            <svg viewBox="0 0 500 160" fill="none" xmlns="http://www.w3.org/2000/svg" className="campus-svg">
              {/* Rolling gentle hill */}
              <path d="M0 160 C120 135 220 130 350 145 C420 152 470 156 500 160 L500 160 L0 160 Z" fill="#14172f" />
              <path d="M0 160 C100 142 200 138 320 150 C400 158 460 159 500 160 L500 160 L0 160 Z" fill="#1e2246" />

              {/* Central Clock Tower */}
              <rect x="235" y="45" width="30" height="95" rx="3" fill="#252a56" />
              <polygon points="250,20 232,45 268,45" fill="#31376e" />
              {/* Spire */}
              <line x1="250" y1="12" x2="250" y2="20" stroke="#a855f7" strokeWidth="2" />
              {/* Clock Face */}
              <circle cx="250" cy="58" r="7" fill="#111328" stroke="#a855f7" strokeWidth="1.5" />
              <line x1="250" y1="58" x2="250" y2="54" stroke="#c084fc" strokeWidth="1.2" strokeLinecap="round" />
              <line x1="250" y1="58" x2="253" y2="58" stroke="#c084fc" strokeWidth="1.2" strokeLinecap="round" />
              {/* Tower Windows */}
              <rect x="242" y="74" width="6" height="12" rx="2" fill="#111328" />
              <rect x="252" y="74" width="6" height="12" rx="2" fill="#111328" />
              <rect x="242" y="94" width="6" height="12" rx="2" fill="#111328" />
              <rect x="252" y="94" width="6" height="12" rx="2" fill="#111328" />
              <rect x="242" y="114" width="6" height="12" rx="2" fill="#111328" />
              <rect x="252" y="114" width="6" height="12" rx="2" fill="#111328" />

              {/* Left Collegiate Wing */}
              <rect x="160" y="75" width="75" height="65" rx="2" fill="#20244c" />
              <polygon points="160,75 197,60 235,75" fill="#2a3064" />
              {/* Windows Wing 1 */}
              <g fill="#111328">
                <rect x="170" y="85" width="8" height="10" rx="1.5" />
                <rect x="185" y="85" width="8" height="10" rx="1.5" />
                <rect x="200" y="85" width="8" height="10" rx="1.5" />
                <rect x="215" y="85" width="8" height="10" rx="1.5" />
                <rect x="170" y="103" width="8" height="10" rx="1.5" />
                <rect x="185" y="103" width="8" height="10" rx="1.5" />
                <rect x="200" y="103" width="8" height="10" rx="1.5" />
                <rect x="215" y="103" width="8" height="10" rx="1.5" />
                <rect x="170" y="121" width="8" height="10" rx="1.5" />
                <rect x="185" y="121" width="8" height="10" rx="1.5" />
                <rect x="200" y="121" width="8" height="10" rx="1.5" />
                <rect x="215" y="121" width="8" height="10" rx="1.5" />
              </g>

              {/* Right Collegiate Wing */}
              <rect x="265" y="75" width="75" height="65" rx="2" fill="#20244c" />
              <polygon points="265,75 302,60 340,75" fill="#2a3064" />
              {/* Windows Wing 2 */}
              <g fill="#111328">
                <rect x="275" y="85" width="8" height="10" rx="1.5" />
                <rect x="290" y="85" width="8" height="10" rx="1.5" />
                <rect x="305" y="85" width="8" height="10" rx="1.5" />
                <rect x="320" y="85" width="8" height="10" rx="1.5" />
                <rect x="275" y="103" width="8" height="10" rx="1.5" />
                <rect x="290" y="103" width="8" height="10" rx="1.5" />
                <rect x="305" y="103" width="8" height="10" rx="1.5" />
                <rect x="320" y="103" width="8" height="10" rx="1.5" />
                <rect x="275" y="121" width="8" height="10" rx="1.5" />
                <rect x="290" y="121" width="8" height="10" rx="1.5" />
                <rect x="305" y="121" width="8" height="10" rx="1.5" />
                <rect x="320" y="121" width="8" height="10" rx="1.5" />
              </g>

              {/* Stylized trees */}
              <circle cx="135" cy="125" r="16" fill="#1b1f42" />
              <circle cx="148" cy="118" r="14" fill="#252a58" />
              <circle cx="360" cy="125" r="17" fill="#1b1f42" />
              <circle cx="375" cy="120" r="13" fill="#252a58" />
            </svg>
          </div>
        </div>

        {/* Right Section: Interactive Login Card */}
        <div className="login-right">
          <div className="login-card">
            {/* Graduation Cap Badge Icon */}
            <div className="login-card-icon-container">
              <div className="login-card-cap-icon">
                <svg width="34" height="34" viewBox="0 0 24 24" fill="none" stroke="#a855f7" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M22 10v6M2 10l10-5 10 5-10 5z" />
                  <path d="M6 12v5c3 3 9 3 12 0v-5" />
                </svg>
              </div>
            </div>

            <h2 className="login-card-title">Welcome Back!</h2>
            <p className="login-card-subtitle">Sign in to access ClashFree</p>

            {/* Notification messages */}
            {errorMessage && (
              <div className="login-alert login-alert-error" role="alert">
                <span>⚠️</span>
                <span>{errorMessage}</span>
              </div>
            )}
            {infoMessage && (
              <div className="login-alert login-alert-info" role="status">
                <span>ℹ️</span>
                <span>{infoMessage}</span>
              </div>
            )}

            {!showForgotPassword ? (
              <form onSubmit={handleSubmit} className="login-form">
                {/* Email Address Field */}
                <div className="login-field-group">
                  <div className="login-input-wrapper">
                    <span className="login-input-icon">
                      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <rect width="20" height="16" x="2" y="4" rx="2" />
                        <path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7" />
                      </svg>
                    </span>
                    <input
                      type="email"
                      className="login-input"
                      placeholder="Email Address"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      autoComplete="email"
                      required
                      disabled={loading}
                    />
                  </div>
                </div>

                {/* Password Field */}
                <div className="login-field-group">
                  <div className="login-input-wrapper">
                    <span className="login-input-icon">
                      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <rect width="18" height="11" x="3" y="11" rx="2" ry="2" />
                        <path d="M7 11V7a5 5 0 0 1 10 0v4" />
                      </svg>
                    </span>
                    <input
                      type={showPassword ? "text" : "password"}
                      className="login-input"
                      placeholder="Password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      autoComplete="current-password"
                      required
                      disabled={loading}
                    />
                    <button
                      type="button"
                      className="login-toggle-password"
                      onClick={() => setShowPassword(!showPassword)}
                      title={showPassword ? "Hide password" : "Show password"}
                      tabIndex="-1"
                    >
                      {showPassword ? (
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                          <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24" />
                          <line x1="1" x2="23" y1="1" y2="23" />
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

                {/* Remember Me & Forgot Password Row */}
                <div className="login-options-row">
                  <label className="login-remember-label">
                    <input
                      type="checkbox"
                      checked={rememberMe}
                      onChange={(e) => setRememberMe(e.target.checked)}
                      className="login-checkbox"
                    />
                    <span>Remember me</span>
                  </label>
                  <button
                    type="button"
                    className="login-forgot-link"
                    onClick={() => {
                      setShowForgotPassword(true);
                      setErrorMessage("");
                      setInfoMessage("");
                    }}
                  >
                    Forgot Password?
                  </button>
                </div>

                {/* Sign In Submit Button */}
                <button
                  type="submit"
                  className="login-submit-btn"
                  disabled={loading}
                >
                  {loading ? (
                    <span className="login-btn-spinner-content">
                      <span className="spinner-circle" /> Authenticating...
                    </span>
                  ) : (
                    <span>Sign In &rarr;</span>
                  )}
                </button>
              </form>
            ) : (
              /* Forgot Password Form */
              <form onSubmit={handleForgotPassword} className="login-form">
                <p className="login-reset-desc">
                  Enter your registered institutional email to receive a password reset link.
                </p>
                <div className="login-field-group">
                  <div className="login-input-wrapper">
                    <span className="login-input-icon">
                      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <rect width="20" height="16" x="2" y="4" rx="2" />
                        <path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7" />
                      </svg>
                    </span>
                    <input
                      type="email"
                      className="login-input"
                      placeholder="Institutional Email"
                      value={resetEmail}
                      onChange={(e) => setResetEmail(e.target.value)}
                      required
                      disabled={resetLoading}
                    />
                  </div>
                </div>

                <button
                  type="submit"
                  className="login-submit-btn"
                  disabled={resetLoading}
                >
                  {resetLoading ? "Dispatching..." : "Send Reset Link"}
                </button>

                <button
                  type="button"
                  className="login-back-btn"
                  onClick={() => {
                    setShowForgotPassword(false);
                    setErrorMessage("");
                  }}
                >
                  &larr; Back to Sign In
                </button>
              </form>
            )}

            {/* Divider "or" */}
            <div className="login-divider">
              <span>or</span>
            </div>

            {/* Secure & Trusted Badge */}
            <div className="login-secure-footer">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" style={{ color: "#a855f7" }}>
                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
                <path d="m9 12 2 2 4-4" />
              </svg>
              <span>Secure & Trusted</span>
            </div>

            {/* Test Credentials / Quick Role Testing Drawer */}
            <div className="login-demo-section">
              <button
                type="button"
                className="login-demo-toggle-btn"
                onClick={() => setShowDemoDrawer(!showDemoDrawer)}
              >
                <span>🔑 Test Credentials & Role Presets</span>
                <span>{showDemoDrawer ? "▲" : "▼"}</span>
              </button>

              {showDemoDrawer && (
                <div className="login-demo-drawer">
                  <p className="login-demo-instruction">
                    Click any role below to prefill credentials (password: <code>ClashFree@2026</code>):
                  </p>
                  <div className="login-demo-cards">
                    {DEMO_ACCOUNTS.map((acc) => (
                      <button
                        key={acc.role}
                        type="button"
                        className="login-demo-badge"
                        onClick={() => selectDemoAccount(acc)}
                      >
                        <div className="demo-badge-top">
                          <span className="demo-role-name">{acc.label}</span>
                          <span className="demo-designation">{acc.designation}</span>
                        </div>
                        <div className="demo-scope-text">{acc.scope}</div>
                        <div className="demo-email-text">{acc.email}</div>
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

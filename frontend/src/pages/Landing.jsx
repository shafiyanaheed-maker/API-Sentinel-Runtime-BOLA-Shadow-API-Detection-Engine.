import "../styles/Landing.css";

import {
  Activity,
  ArrowRight,
  Box,
  LockKeyhole,
  ShieldCheck,
  Zap,
} from "lucide-react";

function Landing({ onGetStarted }) {
  return (
    <div className="landing-page">

      {/* =====================================================
          NAVIGATION
          ===================================================== */}

      <header className="landing-nav">

        <div className="landing-brand">
          <div className="landing-brand-mark">
            <ShieldCheck size={22} strokeWidth={2.2} />
          </div>

          <div>
            <div className="landing-brand-name">
              API<span>-</span>Sentinel
            </div>

            <div className="landing-brand-subtitle">
              RUNTIME SECURITY
            </div>
          </div>
        </div>

        <div className="landing-nav-center">
          <span>PLATFORM</span>
          <span>DETECTION</span>
          <span>DOCUMENTATION</span>
        </div>

        <button
          className="landing-signin"
          onClick={onGetStarted}
        >
          Sign In
        </button>

      </header>


      {/* =====================================================
          MAIN HERO
          ===================================================== */}

      <main className="landing-main">

        <section className="landing-hero">

          <div className="landing-status">
            <span className="landing-status-dot" />
            RUNTIME PROTECTION ENGINE
          </div>

          <h1>
            YOU SHIP.
            <br />
            WE WATCH.
            <br />
            <span>WE BLOCK.</span>
          </h1>

          <p className="landing-description">
            Runtime visibility for APIs that cannot afford blind
            spots. Detect authorization abuse, shadow endpoints,
            and abnormal traffic while it happens.
          </p>

          <div className="landing-actions">

            <button
              className="landing-primary"
              onClick={onGetStarted}
            >
              Open Security Console
              <ArrowRight size={17} />
            </button>

            <button
              className="landing-secondary"
              onClick={onGetStarted}
            >
              Explore Engine
              <ArrowRight size={16} />
            </button>

          </div>

          <div className="landing-micro-status">

            <strong>● LIVE PROTECTION</strong>

            <span className="landing-micro-divider" />

            <span>Traffic monitored</span>

            <span className="landing-micro-divider" />

            <span>Execution-level enforcement</span>

          </div>

        </section>


        {/* =================================================
            SECURITY VISUAL
            ================================================= */}

        <section className="landing-visual">

          <div className="visual-orbit" />

          <div className="visual-core">

            <div className="visual-core-shield">
              <ShieldCheck size={30} strokeWidth={1.8} />
            </div>

            <div className="visual-core-title">
              API-SENTINEL
            </div>

            <div className="visual-core-status">
              <span className="landing-status-dot" />
              ENGINE ACTIVE
            </div>

          </div>


          {/* Threat card */}

          <div className="threat-card threat-card-danger">

            <div className="threat-card-top">

              <div className="threat-icon">
                <LockKeyhole size={15} />
              </div>

              <div>
                <strong>BOLA DETECTED</strong>
                <small>Unauthorized object access</small>
              </div>

            </div>

          </div>


          {/* Safe card */}

          <div className="threat-card threat-card-safe">

            <div className="threat-card-top">

              <div className="threat-icon">
                <ShieldCheck size={15} />
              </div>

              <div>
                <strong>REQUEST VERIFIED</strong>
                <small>Authorization valid</small>
              </div>

            </div>

          </div>


          {/* Threat blocked */}

          <div className="threat-card threat-card-warning">

            <div className="threat-card-top">

              <div className="threat-icon">
                <Zap size={15} />
              </div>

              <div>
                <strong>THREAT BLOCKED</strong>
                <small>Execution prevented</small>
              </div>

            </div>

          </div>


          {/* Request stream */}

          <div className="request-stream">

            <div className="stream-header">

              <span>
                <Activity size={11} />
                LIVE ATTACK SURFACE
              </span>

              <span className="stream-live">
                ● STREAM // 01
              </span>

            </div>


            <div className="stream-row">

              <span className="method">
                GET
              </span>

              <span className="endpoint">
                /api/users/101
              </span>

              <span className="stream-status allowed">
                ALLOWED
              </span>

            </div>


            <div className="stream-row">

              <span className="method">
                GET
              </span>

              <span className="endpoint">
                /api/users/102
              </span>

              <span className="stream-status blocked">
                BLOCKED
              </span>

            </div>


            <div className="stream-row">

              <span className="method">
                POST
              </span>

              <span className="endpoint">
                /api/orders
              </span>

              <span className="stream-status allowed">
                ALLOWED
              </span>

            </div>

          </div>

        </section>

      </main>


      {/* =====================================================
          CAPABILITIES
          ===================================================== */}

      <section className="landing-capabilities">

        <div className="capability">

          <div className="capability-icon">
            <LockKeyhole size={15} />
          </div>

          <div className="capability-text">
            <strong>BOLA</strong>
            <span>Object authorization</span>
          </div>

        </div>


        <div className="capability">

          <div className="capability-icon">
            <ShieldCheck size={15} />
          </div>

          <div className="capability-text">
            <strong>BFLA</strong>
            <span>Function authorization</span>
          </div>

        </div>


        <div className="capability">

          <div className="capability-icon">
            <Box size={15} />
          </div>

          <div className="capability-text">
            <strong>SHADOW APIs</strong>
            <span>Endpoint discovery</span>
          </div>

        </div>


        <div className="capability">

          <div className="capability-icon">
            <Activity size={15} />
          </div>

          <div className="capability-text">
            <strong>RUNTIME</strong>
            <span>Continuous monitoring</span>
          </div>

        </div>


        <div className="capability">

          <div className="capability-icon">
            <Zap size={15} />
          </div>

          <div className="capability-text">
            <strong>ZERO-TRUST</strong>
            <span>Execution-level protection</span>
          </div>

        </div>

      </section>


      {/* =====================================================
          FOOTER
          ===================================================== */}

      <footer className="landing-footer">

        <span>API-Sentinel</span>

        <span>
          Runtime API Security Platform
        </span>

        <span>
          v0.1.0
        </span>

      </footer>

    </div>
  );
}

export default Landing;
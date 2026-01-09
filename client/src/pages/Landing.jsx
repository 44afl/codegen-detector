import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "./landing.css";

export default function Landing() {
  const [mobileMenuActive, setMobileMenuActive] = useState(false);
  const [headerBackground, setHeaderBackground] = useState(false);
  const navigate = useNavigate();

  const handleMobileMenuToggle = () => {
    setMobileMenuActive(!mobileMenuActive);
  };

  const closeMobileMenu = () => {
    setMobileMenuActive(false);
  };

  const handleScroll = () => {
    if (window.pageYOffset > 100) {
      setHeaderBackground(true);
    } else {
      setHeaderBackground(false);
    }
  };

  useEffect(() => {
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  useEffect(() => {
    const elements = document.querySelectorAll(
      ".feature-card, .stat-card, .step"
    );
    const observerOptions = {
      threshold: 0.1,
      rootMargin: "0px 0px -100px 0px",
    };

    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.style.opacity = "1";
          entry.target.style.transform = "translateY(0)";
        }
      });
    }, observerOptions);

    elements.forEach((el) => {
      el.style.opacity = "0";
      el.style.transform = "translateY(20px)";
      el.style.transition = "opacity 0.6s ease, transform 0.6s ease";
      observer.observe(el);
    });

    return () => observer.disconnect();
  }, []);

  const scrollToSection = (id) => {
    const element = document.getElementById(id);
    if (element) {
      element.scrollIntoView({ behavior: "smooth", block: "start" });
    }
    closeMobileMenu();
  };

  return (
    <div className="landing-page">
      <header
        className={`header ${headerBackground ? "scrolled" : ""}`}
        style={
          headerBackground
            ? {
                background: "rgba(10, 10, 20, 0.95)",
                boxShadow: "0 4px 20px rgba(0, 0, 0, 0.3)",
              }
            : {
                background: "rgba(10, 10, 20, 0.8)",
                boxShadow: "none",
              }
        }
      >
        <div className="container">
          <div className="header-content">
            <div className="logo">
              <svg
                width="32"
                height="32"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
              >
                <polyline points="16 18 22 12 16 6"></polyline>
                <polyline points="8 6 2 12 8 18"></polyline>
              </svg>
              <span>CodeGen Detector</span>
            </div>
            <nav className="nav">
              <button
                onClick={() => scrollToSection("features")}
                style={{
                  background: "none",
                  border: "none",
                  cursor: "pointer",
                  color: "inherit",
                }}
              >
                Features
              </button>
              <button
                onClick={() => scrollToSection("how-it-works")}
                style={{
                  background: "none",
                  border: "none",
                  cursor: "pointer",
                  color: "inherit",
                }}
              >
                How It Works
              </button>
              <button
                onClick={() => scrollToSection("pricing")}
                style={{
                  background: "none",
                  border: "none",
                  cursor: "pointer",
                  color: "inherit",
                }}
              >
                Pricing
              </button>
              <button
                className="btn-primary"
                onClick={() => navigate("/signup")}
              >
                Get Started
              </button>
            </nav>
            <button
              className="mobile-menu-btn"
              id="mobileMenuBtn"
              onClick={handleMobileMenuToggle}
            >
              <span></span>
              <span></span>
              <span></span>
            </button>
          </div>
        </div>
      </header>

      <div className={`mobile-menu ${mobileMenuActive ? "active" : ""}`}>
        <button
          onClick={() => {
            scrollToSection("features");
            closeMobileMenu();
          }}
          style={{
            background: "none",
            border: "none",
            cursor: "pointer",
            color: "inherit",
          }}
        >
          Features
        </button>
        <button
          onClick={() => {
            scrollToSection("how-it-works");
            closeMobileMenu();
          }}
          style={{
            background: "none",
            border: "none",
            cursor: "pointer",
            color: "inherit",
          }}
        >
          How It Works
        </button>
        <button
          onClick={() => {
            scrollToSection("pricing");
            closeMobileMenu();
          }}
          style={{
            background: "none",
            border: "none",
            cursor: "pointer",
            color: "inherit",
          }}
        >
          Pricing
        </button>
        <button
          className="btn-primary"
          onClick={() => {
            navigate("/signup");
            closeMobileMenu();
          }}
        >
          Get Started
        </button>
      </div>

      <section className="hero">
        <div className="container">
          <div className="hero-content">
            <div className="hero-text">
              <div className="badge">Powered by Advanced AI</div>
              <h1>Detect AI-Generated Code with Precision</h1>
              <p>
                CodeGen Detector uses state-of-the-art machine learning to
                analyze code patterns and determine whether your code was
                written by humans or generated by AI tools.
              </p>
              <div className="hero-buttons">
                <button
                  className="btn-primary btn-large"
                  onClick={() => navigate("/signup")}
                >
                  Try Free Demo
                </button>
                <button
                  className="btn-secondary btn-large"
                  onClick={() => navigate("/terms")}
                >
                  View Documentation
                </button>
              </div>
              <div className="hero-stats">
                <div className="stat-item">
                  <div className="stat-value">98.7%</div>
                  <div className="stat-label">Accuracy</div>
                </div>
                <div className="stat-item">
                  <div className="stat-value">50+</div>
                  <div className="stat-label">Languages</div>
                </div>
                <div className="stat-item">
                  <div className="stat-value">&lt;2s</div>
                  <div className="stat-label">Analysis Time</div>
                </div>
              </div>
            </div>
            <div className="hero-visual">
              <div className="code-mockup">
                <div className="code-header">
                  <span className="code-dot"></span>
                  <span className="code-dot"></span>
                  <span className="code-dot"></span>
                  <span className="code-title">analysis.js</span>
                </div>
                <div className="code-content">
                  <div className="code-line">
                    <span className="keyword">function</span>
                    {" "}
                    <span className="function">calculateTotal</span>
                    (<span className="param">items</span>) {"{"}
                  </div>
                  <div className="code-line">
                    {"  "}
                    <span className="keyword">return</span>
                    {" items."}
                    <span className="method">reduce</span>
                    {"(("}
                    <span className="param">sum, item</span>
                    {") => {"}
                  </div>
                  <div className="code-line">
                    {"    "}
                    <span className="keyword">return</span>
                    {" sum + item.price;"}
                  </div>
                  <div className="code-line">
                    {"  "}, <span className="number">0</span>);
                  </div>
                  <div className="code-line">{"}"}</div>
                  <div className="code-line"></div>
                  <div className="code-line analysis-result">
                    <span className="result-icon">✓</span>
                    <span className="result-text">Human-written</span>
                    <span className="confidence">96.3% confidence</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="stats-section">
        <div className="container">
          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-number">1M+</div>
              <div className="stat-description">Code snippets analyzed</div>
            </div>
            <div className="stat-card">
              <div className="stat-number">15K+</div>
              <div className="stat-description">Developers trust us</div>
            </div>
            <div className="stat-card">
              <div className="stat-number">98.7%</div>
              <div className="stat-description">Detection accuracy</div>
            </div>
            <div className="stat-card">
              <div className="stat-number">24/7</div>
              <div className="stat-description">API availability</div>
            </div>
          </div>
        </div>
      </section>

      <section className="features" id="features">
        <div className="container">
          <div className="section-header">
            <h2>Powerful Features for Code Analysis</h2>
            <p>
              Everything you need to detect AI-generated code with confidence
            </p>
          </div>
          <div className="features-grid">
            <div className="feature-card">
              <div className="feature-icon">
                <svg
                  width="24"
                  height="24"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                >
                  <circle cx="12" cy="12" r="10"></circle>
                  <path d="M12 6v6l4 2"></path>
                </svg>
              </div>
              <h3>Real-Time Analysis</h3>
              <p>
                Get instant results on code authenticity with our lightning-fast
                detection engine powered by advanced neural networks.
              </p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">
                <svg
                  width="24"
                  height="24"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                >
                  <polyline points="16 18 22 12 16 6"></polyline>
                  <polyline points="8 6 2 12 8 18"></polyline>
                </svg>
              </div>
              <h3>Multi-Language Support</h3>
              <p>
                Analyze code across 50+ programming languages including Python,
                JavaScript, Java, C++, and more.
              </p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">
                <svg
                  width="24"
                  height="24"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                >
                  <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
                </svg>
              </div>
              <h3>Privacy First</h3>
              <p>
                Your code never leaves your environment. Run analysis locally or
                through our secure, encrypted API.
              </p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">
                <svg
                  width="24"
                  height="24"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                >
                  <line x1="12" y1="1" x2="12" y2="23"></line>
                  <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path>
                </svg>
              </div>
              <h3>Detailed Reports</h3>
              <p>
                Receive comprehensive analysis reports with confidence scores,
                pattern breakdowns, and actionable insights.
              </p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">
                <svg
                  width="24"
                  height="24"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                >
                  <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                  <line x1="9" y1="9" x2="15" y2="15"></line>
                  <line x1="15" y1="9" x2="9" y2="15"></line>
                </svg>
              </div>
              <h3>Batch Processing</h3>
              <p>
                Analyze entire repositories or multiple files simultaneously with
                our powerful batch processing capabilities.
              </p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">
                <svg
                  width="24"
                  height="24"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                >
                  <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path>
                </svg>
              </div>
              <h3>API Integration</h3>
              <p>
                Seamlessly integrate CodeGen Detector into your CI/CD pipeline
                with our developer-friendly REST API.
              </p>
            </div>
          </div>
        </div>
      </section>

      <section className="how-it-works" id="how-it-works">
        <div className="container">
          <div className="section-header">
            <h2>How It Works</h2>
            <p>Advanced machine learning in three simple steps</p>
          </div>
          <div className="steps">
            <div className="step">
              <div className="step-number">01</div>
              <div className="step-content">
                <h3>Submit Your Code</h3>
                <p>
                  Upload code files, paste snippets, or integrate via API. Our
                  system accepts all major programming languages and frameworks.
                </p>
              </div>
            </div>
            <div className="step">
              <div className="step-number">02</div>
              <div className="step-content">
                <h3>AI Analysis</h3>
                <p>
                  Our neural network analyzes patterns, syntax, structure, and
                  coding style against billions of human and AI-generated code
                  samples.
                </p>
              </div>
            </div>
            <div className="step">
              <div className="step-number">03</div>
              <div className="step-content">
                <h3>Get Results</h3>
                <p>
                  Receive detailed reports with confidence scores, pattern
                  analysis, and insights about the code's origin in seconds.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="cta">
        <div className="container">
          <div className="cta-content">
            <h2>Ready to Verify Your Code?</h2>
            <p>
              Join thousands of developers and companies using CodeGen Detector
              to ensure code authenticity
            </p>
            <div className="cta-buttons">
              <button
                className="btn-primary btn-large"
                onClick={() => navigate("/signup")}
              >
                Start Free Trial
              </button>
              <button
                className="btn-secondary btn-large"
                onClick={() => navigate("/subscriptions")}
              >
                Schedule Demo
              </button>
            </div>
          </div>
        </div>
      </section>

      <footer className="footer">
        <div className="container">
          <div className="footer-content">
            <div className="footer-section">
              <div className="footer-logo">
                <svg
                  width="32"
                  height="32"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                >
                  <polyline points="16 18 22 12 16 6"></polyline>
                  <polyline points="8 6 2 12 8 18"></polyline>
                </svg>
                <span>CodeGen Detector</span>
              </div>
              <p>Advanced AI-powered code authenticity detection for the modern developer.</p>
            </div>
            <div className="footer-section">
              <h4>Product</h4>
              <button
                onClick={() => scrollToSection("features")}
                style={{
                  background: "none",
                  border: "none",
                  cursor: "pointer",
                  color: "inherit",
                  textAlign: "left",
                }}
              >
                Features
              </button>
              <button
                onClick={() => scrollToSection("pricing")}
                style={{
                  background: "none",
                  border: "none",
                  cursor: "pointer",
                  color: "inherit",
                  textAlign: "left",
                }}
              >
                Pricing
              </button>
            </div>
            <div className="footer-section">
              <h4>Company</h4>
              <a href="#about">About Us</a>
              <a href="#blog">Blog</a>
              <a href="#careers">Careers</a>
              <a href="#contact">Contact</a>
            </div>
            <div className="footer-section">
              <h4>Legal</h4>
              <button
                onClick={() => navigate("/privacy")}
                style={{
                  background: "none",
                  border: "none",
                  cursor: "pointer",
                  color: "inherit",
                  textAlign: "left",
                }}
              >
                Privacy Policy
              </button>
              <button
                onClick={() => navigate("/terms")}
                style={{
                  background: "none",
                  border: "none",
                  cursor: "pointer",
                  color: "inherit",
                  textAlign: "left",
                }}
              >
                Terms of Service
              </button>
            </div>
          </div>
          <div className="footer-bottom">
            <p>&copy; 2026 CodeGen Detector. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}

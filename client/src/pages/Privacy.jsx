import { Link } from "react-router-dom";

export default function Privacy() {
  return (
    <div className="legal-page">
      <div className="container">
        <h1>Privacy Policy</h1>
        <p className="last-updated">Last Updated: January 9, 2026</p>

        <section>
          <h2>1. Information We Collect</h2>
          <p>
            We collect information that you provide directly to us, including:
          </p>
          <ul>
            <li>Email address and password (encrypted)</li>
            <li>Full name (optional)</li>
            <li>Code snippets you submit for analysis</li>
            <li>Usage data and analytics</li>
          </ul>
        </section>

        <section>
          <h2>2. How We Use Your Information</h2>
          <p>We use the information we collect to:</p>
          <ul>
            <li>Provide, maintain, and improve our services</li>
            <li>Process your transactions and send related information</li>
            <li>Send you technical notices and support messages</li>
            <li>Respond to your comments and questions</li>
            <li>Improve our machine learning models</li>
          </ul>
        </section>

        <section>
          <h2>3. Information Sharing</h2>
          <p>
            We do not sell, trade, or rent your personal information to third
            parties. We may share your information only in the following
            circumstances:
          </p>
          <ul>
            <li>With your consent</li>
            <li>To comply with legal obligations</li>
            <li>To protect our rights and prevent fraud</li>
          </ul>
        </section>

        <section>
          <h2>4. Data Security</h2>
          <p>
            We implement appropriate security measures to protect your personal
            information. However, no method of transmission over the Internet is
            100% secure.
          </p>
        </section>

        <section>
          <h2>5. Code Analysis</h2>
          <p>
            Code you submit for analysis is processed by our AI models and may be
            stored temporarily for processing purposes. We do not share your code
            with third parties.
          </p>
        </section>

        <section>
          <h2>6. Cookies and Tracking</h2>
          <p>
            We use cookies and similar tracking technologies to track activity on
            our service and store certain information for session management and
            analytics.
          </p>
        </section>

        <section>
          <h2>7. Your Rights</h2>
          <p>You have the right to:</p>
          <ul>
            <li>Access your personal data</li>
            <li>Correct inaccurate data</li>
            <li>Request deletion of your data</li>
            <li>Object to data processing</li>
            <li>Export your data</li>
          </ul>
        </section>

        <section>
          <h2>8. Data Retention</h2>
          <p>
            We retain your personal information for as long as necessary to
            provide our services and comply with legal obligations.
          </p>
        </section>

        <section>
          <h2>9. Children's Privacy</h2>
          <p>
            Our service is not directed to children under 13. We do not knowingly
            collect personal information from children under 13.
          </p>
        </section>

        <section>
          <h2>10. Changes to Privacy Policy</h2>
          <p>
            We may update this Privacy Policy from time to time. We will notify
            you of any changes by updating the "Last Updated" date.
          </p>
        </section>

        <section>
          <h2>11. Contact Us</h2>
          <p>
            If you have questions about this Privacy Policy, please contact us at
            privacy@codegendetector.com
          </p>
        </section>

        <div className="auth-links">
          <Link to="/">Back to Home</Link>
          <Link to="/terms">Terms of Service</Link>
        </div>
      </div>
    </div>
  );
}

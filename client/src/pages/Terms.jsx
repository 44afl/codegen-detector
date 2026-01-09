import { Link } from "react-router-dom";

export default function Terms() {
  return (
    <div className="legal-page">
      <div className="container">
        <h1>Terms of Service</h1>
        <p className="last-updated">Last Updated: January 9, 2026</p>

        <section>
          <h2>1. Acceptance of Terms</h2>
          <p>
            By accessing and using CodeGen Detector, you accept and agree to be
            bound by the terms and provision of this agreement.
          </p>
        </section>

        <section>
          <h2>2. Use License</h2>
          <p>
            Permission is granted to temporarily access the service for personal,
            non-commercial transitory viewing only. This is the grant of a
            license, not a transfer of title.
          </p>
        </section>

        <section>
          <h2>3. Service Description</h2>
          <p>
            CodeGen Detector provides AI-powered code analysis to determine
            whether code is machine-generated or human-written. The service is
            provided "as is" without warranties of any kind.
          </p>
        </section>

        <section>
          <h2>4. User Accounts</h2>
          <p>
            You are responsible for maintaining the confidentiality of your
            account and password. You agree to accept responsibility for all
            activities that occur under your account.
          </p>
        </section>

        <section>
          <h2>5. Subscriptions</h2>
          <p>
            Some parts of the Service are billed on a subscription basis. You
            will be billed in advance on a recurring and periodic basis.
          </p>
        </section>

        <section>
          <h2>6. Refunds</h2>
          <p>
            Certain refund requests for subscriptions may be considered on a
            case-by-case basis and granted at the sole discretion of CodeGen
            Detector.
          </p>
        </section>

        <section>
          <h2>7. Prohibited Uses</h2>
          <p>
            You may not use our service for any illegal purposes or to violate
            any laws. You may not attempt to compromise the security of our
            systems.
          </p>
        </section>

        <section>
          <h2>8. Limitation of Liability</h2>
          <p>
            In no event shall CodeGen Detector be liable for any indirect,
            incidental, special, consequential or punitive damages arising out of
            your use of the service.
          </p>
        </section>

        <section>
          <h2>9. Changes to Terms</h2>
          <p>
            We reserve the right to modify these terms at any time. We will
            notify users of any changes by updating the "Last Updated" date.
          </p>
        </section>

        <section>
          <h2>10. Contact</h2>
          <p>
            If you have any questions about these Terms, please contact us at
            support@codegendetector.com
          </p>
        </section>

        <div className="auth-links">
          <Link to="/">Back to Home</Link>
          <Link to="/privacy">Privacy Policy</Link>
        </div>
      </div>
    </div>
  );
}

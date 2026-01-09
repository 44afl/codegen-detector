import { useState, useEffect } from "react";
import { Link } from "react-router-dom";

export default function Subscriptions() {
  const [plans, setPlans] = useState([]);
  const [currentSubscription, setCurrentSubscription] = useState(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  useEffect(() => {
    fetchPlans();
    fetchCurrentSubscription();
  }, []);

  const fetchPlans = async () => {
    try {
      const res = await fetch("http://localhost:5050/subscriptions/plans");
      const data = await res.json();
      setPlans(data.plans || []);
    } catch (err) {
      console.error("Failed to fetch plans:", err);
    }
  };

  const fetchCurrentSubscription = async () => {
    const token = localStorage.getItem("session_token");
    if (!token) return;

    try {
      const res = await fetch("http://localhost:5050/auth/me", {
        headers: { Authorization: `Bearer ${token}` },
      });
      const data = await res.json();
      setCurrentSubscription(data.subscription);
    } catch (err) {
      console.error("Failed to fetch subscription:", err);
    }
  };

  const handleSubscribe = async (planType) => {
    const token = localStorage.getItem("session_token");
    if (!token) {
      window.location.href = "/login";
      return;
    }

    setLoading(true);
    setMessage("");

    try {
      const res = await fetch("http://localhost:5050/subscriptions/subscribe", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ plan_type: planType }),
      });

      const data = await res.json();

      if (res.ok) {
        setMessage("Subscription activated successfully!");
        fetchCurrentSubscription();
      } else {
        setMessage(data.error || "Failed to subscribe");
      }
    } catch (err) {
      setMessage("Network error. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = async () => {
    const token = localStorage.getItem("session_token");
    if (!token) return;

    setLoading(true);

    try {
      const res = await fetch("http://localhost:5050/subscriptions/cancel", {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
      });

      if (res.ok) {
        setMessage("Subscription canceled");
        fetchCurrentSubscription();
      }
    } catch (err) {
      setMessage("Failed to cancel subscription");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="subscriptions-page">
      <div className="container">
        <h1>Subscription Plans</h1>

        {message && <div className="success-message">{message}</div>}

        {currentSubscription && (
          <div className="current-subscription">
            <h3>Current Subscription</h3>
            <p>
              <strong>Plan:</strong> {currentSubscription.plan_type}
            </p>
            <p>
              <strong>Status:</strong> {currentSubscription.status}
            </p>
            <p>
              <strong>Expires:</strong>{" "}
              {new Date(currentSubscription.end_date).toLocaleDateString()}
            </p>
            {currentSubscription.status === "active" && (
              <button
                onClick={handleCancel}
                className="btn-danger"
                disabled={loading}
              >
                Cancel Subscription
              </button>
            )}
          </div>
        )}

        <div className="plans-grid">
          {plans.map((plan) => (
            <div key={plan.id} className="plan-card">
              <h2>{plan.name}</h2>
              <div className="price">
                ${plan.price}
                <span>/month</span>
              </div>
              <ul className="features">
                {plan.features.map((feature, idx) => (
                  <li key={idx}>{feature}</li>
                ))}
              </ul>
              <button
                onClick={() => handleSubscribe(plan.id)}
                className="btn-primary"
                disabled={loading}
              >
                {currentSubscription?.plan_type === plan.id
                  ? "Current Plan"
                  : "Subscribe"}
              </button>
            </div>
          ))}
        </div>

        <div className="auth-links">
          <Link to="/">Back to Home</Link>
        </div>
      </div>
    </div>
  );
}

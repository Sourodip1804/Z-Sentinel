import { useState } from "react";

const INITIAL = {
  amount: "125.00",
  currency: "USD",
  merchant_category: "online",
  hour_of_day: "14",
  device_novelty: "0",
  location_deviation: "0.20",
  transaction_velocity: "2",
  unusual_time: "0",
  channel: "online",
};

export default function TransactionForm({ onPredict, loading }) {
  const [form, setForm] = useState(INITIAL);
  const [error, setError] = useState("");

  function update(event) {
    setForm((current) => ({ ...current, [event.target.name]: event.target.value }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    const amount = Number(form.amount);
    if (!Number.isFinite(amount) || amount <= 0) {
      setError("Amount must be a number greater than 0.");
      return;
    }
    setError("");
    await onPredict({
      amount,
      currency: form.currency,
      merchant_category: form.merchant_category,
      hour_of_day: Number(form.hour_of_day),
      device_novelty: Number(form.device_novelty),
      location_deviation: Number(form.location_deviation),
      transaction_velocity: Number(form.transaction_velocity),
      unusual_time: Number(form.unusual_time),
      channel: form.channel,
      source: "api",
    });
  }

  return (
    <section className="panel">
      <h2>Score a transaction</h2>
      <p className="panel-copy">
        Fields map to feature contract <code>txn_features_v1</code>. Only
        pre-decision inputs are sent.
      </p>
      <form className="txn-form" onSubmit={handleSubmit}>
        <label>
          Amount
          <input
            name="amount"
            type="number"
            min="0.01"
            step="0.01"
            value={form.amount}
            onChange={update}
            required
          />
        </label>
        <label>
          Currency
          <input
            name="currency"
            maxLength={3}
            value={form.currency}
            onChange={update}
          />
        </label>
        <label>
          Merchant category
          <select
            name="merchant_category"
            value={form.merchant_category}
            onChange={update}
          >
            <option value="grocery">grocery</option>
            <option value="electronics">electronics</option>
            <option value="travel">travel</option>
            <option value="restaurant">restaurant</option>
            <option value="fuel">fuel</option>
            <option value="online">online</option>
            <option value="other">other</option>
          </select>
        </label>
        <label>
          Hour of day (0-23)
          <input
            name="hour_of_day"
            type="number"
            min="0"
            max="23"
            value={form.hour_of_day}
            onChange={update}
          />
        </label>
        <label>
          Device novelty (0-1)
          <input
            name="device_novelty"
            type="number"
            min="0"
            max="1"
            step="0.01"
            value={form.device_novelty}
            onChange={update}
          />
        </label>
        <label>
          Location deviation (0-1)
          <input
            name="location_deviation"
            type="number"
            min="0"
            max="1"
            step="0.01"
            value={form.location_deviation}
            onChange={update}
          />
        </label>
        <label>
          Transaction velocity
          <input
            name="transaction_velocity"
            type="number"
            min="0"
            value={form.transaction_velocity}
            onChange={update}
          />
        </label>
        <label>
          Unusual time (0-1)
          <input
            name="unusual_time"
            type="number"
            min="0"
            max="1"
            step="0.01"
            value={form.unusual_time}
            onChange={update}
          />
        </label>
        <label>
          Channel
          <select name="channel" value={form.channel} onChange={update}>
            <option value="online">online</option>
            <option value="pos">pos</option>
            <option value="atm">atm</option>
            <option value="other">other</option>
          </select>
        </label>
        {error ? <p className="form-error">{error}</p> : null}
        <button className="primary-btn" type="submit" disabled={loading}>
          {loading ? "Scoring…" : "Run prediction"}
        </button>
      </form>
    </section>
  );
}

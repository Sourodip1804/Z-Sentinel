import { useState, useEffect } from "react";
import {
  getStats,
  getTransactions,
  getRisk,
  simulateTransaction,
  predictTransaction,
} from "./api";
import "./App.css"
import Header from "./components/Header";
import StatCard from "./components/StatCard";
import TransactionForm from "./components/TransactionForm";
import RiskChart from "./components/RiskChart";
import TransactionTable from "./components/TransactionTable";

export default function App() {
  const [stats, setStats] = useState(null);
  const [risk, setRisk] = useState(null);
  const [transactions, setTransactions] = useState([]);
  const [online, setOnline] = useState(false);
  const [loading, setLoading] = useState(false);
  const [lastResult, setLastResult] = useState(null);

  // Fetch all dashboard data
  async function refresh() {
    try {
      const [statsRes, txRes, riskRes] = await Promise.all([
        getStats(),
        getTransactions(),
        getRisk(),
      ]);

      setStats(statsRes.data);
      setTransactions(txRes.data);
      setRisk(riskRes.data);
      setOnline(true);
    } catch (error) {
      console.error("Refresh failed:", error);
      setOnline(false);
    }
  }

  // Refresh every 4 seconds
  useEffect(() => {
    refresh();
    const timer = setInterval(refresh, 4000);
    return () => clearInterval(timer);
  }, []);

  // Simulate a random transaction
  async function simulate() {
    setLoading(true);
    try {
      const response = await simulateTransaction();
      setLastResult(response.data);
      await refresh();
    } catch (error) {
      console.error("Simulation failed:", error);
    } finally {
      setLoading(false);
    }
  }

  // Custom prediction
  async function predict(payload) {
    setLoading(true);
    try {
      const response = await predictTransaction(payload);
      setLastResult(response.data);
      await refresh();
    } catch (error) {
      console.error("Prediction failed:", error);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <Header online={online} onSimulate={simulate} loading={loading} />

      <StatCard
        title="Total transactions"
        value={stats?.total_transaction ?? 0}
      />
      <StatCard
        title="High-risk"
        value={stats?.high_risk_transaction ?? 0}
      />
      <StatCard title="Approved" value={stats?.approved ?? 0} />
      <StatCard title="Blocked" value={stats?.blocked ?? 0} />

      <TransactionForm onPredict={predict} loading={loading} />

      {lastResult && (
        <pre>{JSON.stringify(lastResult, null, 2)}</pre>
      )}

      <RiskChart risk={risk} />
      <TransactionTable transactions={transactions} />
    </div>
  );
}
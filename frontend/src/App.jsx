import { useCallback, useEffect, useState } from "react";
import {
  getHealth,
  getRisk,
  getStats,
  getTransactions,
  predictTransaction,
  simulateTransaction,
} from "./api";
import "./App.css";
import DecisionChart from "./components/DecisionChart";
import Header from "./components/Header";
import LatestPrediction from "./components/LatestPrediction";
import ModelStatus from "./components/ModelStatus";
import RiskChart from "./components/RiskChart";
import StatCard from "./components/StatCard";
import TransactionForm from "./components/TransactionForm";
import TransactionTable from "./components/TransactionTable";
import VolumeChart from "./components/VolumeChart";

const PAGE_SIZE = 10;

export default function App() {
  const [stats, setStats] = useState(null);
  const [risk, setRisk] = useState(null);
  const [transactions, setTransactions] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [riskFilter, setRiskFilter] = useState("");
  const [decisionFilter, setDecisionFilter] = useState("");
  const [online, setOnline] = useState(false);
  const [loading, setLoading] = useState(false);
  const [tableLoading, setTableLoading] = useState(false);
  const [tableError, setTableError] = useState("");
  const [lastResult, setLastResult] = useState(null);
  const [predictError, setPredictError] = useState("");
  const [scenario, setScenario] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);

  const refreshCore = useCallback(async () => {
    try {
      const [statsRes, riskRes] = await Promise.all([getStats(), getRisk()]);
      setStats(statsRes.data);
      setRisk(riskRes.data);
    } catch {
      // Handled silently
    }
  }, []);

  const refreshTable = useCallback(async () => {
    setTableLoading(true);
    setTableError("");
    try {
      const params = { page, page_size: PAGE_SIZE };
      if (riskFilter) params.risk_level = riskFilter;
      if (decisionFilter) params.decision = decisionFilter;
      const response = await getTransactions(params);
      setTransactions(response.data.items || []);
      setTotal(response.data.total || 0);
    } catch (error) {
      setTableError(error.response?.data?.detail || "Could not load transactions.");
      setTransactions([]);
    } finally {
      setTableLoading(false);
    }
  }, [page, riskFilter, decisionFilter]);

  const refreshAll = useCallback(async () => {
    try {
      await Promise.all([refreshCore(), refreshTable()]);
      const health = await getHealth();
      setOnline(Boolean(health.data?.model_ready && health.data?.mongodb_ready));
    } catch {
      setOnline(false);
    }
  }, [refreshCore, refreshTable]);

  useEffect(() => {
    refreshAll();
  }, [refreshAll]);

  useEffect(() => {
    const timer = setInterval(async () => {
      try {
        const health = await getHealth();
        setOnline(Boolean(health.data?.model_ready && health.data?.mongodb_ready));
      } catch {
        setOnline(false);
      }
    }, 10000);
    return () => clearInterval(timer);
  }, []);

  // Continuous real-time transaction simulation loop
  useEffect(() => {
    if (!isStreaming) return;
    const interval = setInterval(async () => {
      try {
        const payload = scenario ? { scenario } : {};
        const response = await simulateTransaction(payload);
        setLastResult(response.data);
        await refreshAll();
      } catch (err) {
        console.error("Stream simulation error:", err);
      }
    }, 3500);
    return () => clearInterval(interval);
  }, [isStreaming, scenario, refreshAll]);

  async function simulate() {
    setLoading(true);
    setPredictError("");
    try {
      const payload = scenario ? { scenario } : {};
      const response = await simulateTransaction(payload);
      setLastResult(response.data);
      await refreshAll();
    } catch (error) {
      setPredictError(error.response?.data?.detail || "Simulation failed. Is the backend running?");
    } finally {
      setLoading(false);
    }
  }

  async function predict(payload) {
    setLoading(true);
    setPredictError("");
    try {
      const response = await predictTransaction(payload);
      setLastResult(response.data);
      await refreshAll();
    } catch (error) {
      setPredictError(error.response?.data?.detail || "Prediction failed.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="app">
      <Header
        online={online}
        onSimulate={simulate}
        loading={loading}
        scenario={scenario}
        onScenarioChange={setScenario}
        isStreaming={isStreaming}
        onToggleStreaming={() => setIsStreaming(!isStreaming)}
      />
      <main className="dashboard">
        <ModelStatus />

        <section className="stats-grid">
          <StatCard title="Total transactions" value={stats?.total_transactions ?? 0} />
          <StatCard title="High-risk" value={stats?.high_risk_transactions ?? 0} />
          <StatCard title="Approved" value={stats?.approved ?? 0} />
          <StatCard title="Review" value={stats?.review ?? 0} />
          <StatCard title="Blocked" value={stats?.blocked ?? 0} />
          <StatCard
            title="Avg inference"
            value={`${stats?.average_inference_ms ?? 0} ms`}
          />
        </section>

        <section className="charts-grid">
          <div className="panel">
            <h2>Risk distribution</h2>
            <RiskChart risk={risk} loading={tableLoading && !risk} />
          </div>
          <div className="panel">
            <h2>Decision distribution</h2>
            <DecisionChart stats={stats} loading={!stats} />
          </div>
          <div className="panel">
            <h2>Recent volume by minute (UTC)</h2>
            <VolumeChart transactions={transactions} />
          </div>
        </section>

        <div className="content-grid">
          <TransactionForm onPredict={predict} loading={loading} />
          <LatestPrediction result={lastResult} error={predictError} />
        </div>

        <TransactionTable
          transactions={transactions}
          total={total}
          page={page}
          pageSize={PAGE_SIZE}
          loading={tableLoading}
          error={tableError}
          riskFilter={riskFilter}
          decisionFilter={decisionFilter}
          onRiskFilter={(value) => {
            setPage(1);
            setRiskFilter(value);
          }}
          onDecisionFilter={(value) => {
            setPage(1);
            setDecisionFilter(value);
          }}
          onPageChange={setPage}
          onSelect={setLastResult}
        />
      </main>
    </div>
  );
}

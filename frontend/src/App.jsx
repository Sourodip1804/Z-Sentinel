import { useState, useEffect } from "react";
import {getStats, getTransactions, getRisk, simulateTransaction, predictTransaction} from "./api"
import Header from "./components/Header"
import StatCard from "./components/StatCard"
import TransactionForm from "./components/TransactionForm"

const [stats, setStats] = useState(null)
const [risk, setRisk] = useState(null)
const [transactions, setTransactions] = useState([])
const [online, setOnline] = useState(false)
const [loading, setLoading] = useState(false)
const [lastResult, setLastResult] = useState(null)


// making function for the refresh

async function refresh(){
  try{
    const[statsRes, txRes, riskRes] = await Promise.all([getStats(),getTransactions(),getRisk()
    ]);

    setStats(
            statsRes.data
        );

        setTransactions(
            txRes.data
        );

        setRisk(
            riskRes.data
        );

        setOnline(true);

    }

    catch (error) {
        setOnline(false);
  }
}

// for the refresh of the data for every 4 seconds

useEffect(()=>{
  refresh();
  const timer = setInterval(refresh, 4000)
  return()=>{
    clearInterval(timer)
  }
},[]);

// for the simulate the transaction 

async function simulate(){
  setLoading(true);
  try{
    const response= await simulateTransaction()
    setLastResult(response.data)
    await refresh()
  }
  finally{
    setLoading(false)
  }

}


// for the custom prediction engine
async function predict(payload){
  setLoading(true)
  try{
    const response = await predictTransaction(payload)
    setLastResult(response.data)
    await refresh()

  }
  finally{
    setLoading(false);
  }
}

<Header
  online={online}
  onSimulate={simulate}
  loading={loading}
/>

<StatCard
  title="Total transactions"
  value={stats?.total_transaction ?? 0}
/>

<StatCard
  title="High-risk"
  value={stats?.high_risk_transaction ?? 0}
/>

<StatCard
    title="Approved"
    value={stats?.approved ?? 0}
/>

<StatCard
    title="Blocked"
    value={stats?.blocked ?? 0}
/>

<TransactionForm
    onPredict={predict}
    loading={loading}
/>

<RiskChart
    risk={risk}
/>

<TransactionTable
    transactions={transactions}
/>


import {
    ResponsiveContainer,PieChart,Pie,Cell,Tooltip,Legend
} from "recharts";

const data = [
  {
    name: "Low"
    value:  risk?.LOW || 0
  },
  {
        name: "Medium",
        value: risk?.MEDIUM || 0
    },

    {
        name: "High",
        value: risk?.HIGH || 0
    }
]




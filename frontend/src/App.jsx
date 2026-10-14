import { useState, useEffect } from "react";
import {getStats, getTransactions, getRisk, simulateTransaction, predictTransaction} from "./api"

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
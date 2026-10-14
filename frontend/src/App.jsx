import { useState, useEffect } from "react";
import {getStats, getTransactions, getRisk, simulateTransaction, predictTransaction} from "./api"

const [stats, setStats] = useState(null)
const [risk, setRisk] = useState(null)
const [transactions, setTransactions] = useState([])
const [online, setOnline] = useState(false)
const [loading, setLoading] = useState(false)
const [lastResult, setLastResult] = useState(null)


// making function for the refresh

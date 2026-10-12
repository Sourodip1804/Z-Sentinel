import axios from "axios"


const api = axios.create({baseURL:"http://127.0.0.1:8000/api"});

// now creating the arrow function for fetching the api 
export const getStats = ()=>{
    api.get("/stats");
}
export const getTransactions = ()=>{
    api.get("/transactions?limit=30");
}
export const getRisk = ()=>{
    api.get("/risk");
}

// now for sending the data to the api 
export const simulateTransaction = ()=>{
    api.post("/transactions/simulate");
}
export const predictTransaction = (payload)=>{
    api.post("/predict", payload);
}
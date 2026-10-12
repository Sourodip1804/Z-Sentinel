import axios from "axios"


const api = axios.create({baseURL:"http://127.0.0.1:8000/api"});

// now creating the arrow function for fetching the api 
export const getStats = ()=>{
    api.get("/stats");
}
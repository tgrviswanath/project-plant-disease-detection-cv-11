import axios from "axios";
const api = axios.create({ baseURL: process.env.REACT_APP_API_URL || "http://localhost:8000" });
export const predictDisease = (fd) =>
  api.post("/api/v1/predict", fd, { headers: { "Content-Type": "multipart/form-data" } });

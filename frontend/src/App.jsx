// src/App.jsx
import { Routes, Route } from "react-router-dom";
import LoginPage from "./pages/login/LoginPage";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<LoginPage />} />
      <Route path="/login" element={<LoginPage />} />
    </Routes>
  );
}
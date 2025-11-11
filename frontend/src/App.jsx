// src/App.jsx
import { Routes, Route } from "react-router-dom";
import LoginPage from "./pages/login/LoginPage";
import HomePage from "./pages/Home"

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/login" element={<LoginPage />} />
    </Routes>
  );
}
import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import LoginForm from "../../components/forms/LoginForm";
import { loginUser } from "../../api/auth";

export default function LoginPage() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async ({ email, password }) => {
    setError("");
    setLoading(true);
    try {
      const data = await loginUser(email, password);
      localStorage.setItem("access_token", data.access_token);
      if (data.user) localStorage.setItem("user", JSON.stringify(data.user));
      navigate("/", { replace: true });
    } catch {
      setError("Credenciais inválidas ou erro na autenticação.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <LoginForm
      onSubmit={handleSubmit}
      loading={loading}
      errorMessage={error}
    />
  );
}

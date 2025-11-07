import { useNavigate } from "react-router-dom";
import LoginForm from "../../components/forms/LoginForm";

export default function LoginPage() {
  const navigate = useNavigate();

  const handleSubmit = async ({ email, password }) => {
    try {
      const response = await fetch("http://localhost:8000/api/v1/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        alert(errorData.detail || "Erro ao fazer login");
        return;
      }

      const data = await response.json();
      // Retirar console.log. Feito apenas para depuração em dev
      console.log("✅ Login bem-sucedido:", data);

      localStorage.setItem("access_token", data.access_token);
      localStorage.setItem("refresh_token", data.refresh_token);
      localStorage.setItem("user", JSON.stringify(data.user));

      navigate("/");
    } catch (error) {
      console.error("Erro:", error);
      alert("Erro de conexão com o servidor");
    }
  };

  return <LoginForm onSubmit={handleSubmit} />;
}
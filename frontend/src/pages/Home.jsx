import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import "../App.css";
import { handleApi } from "../api/handleApi";

const Home = () => {
  const navigate = useNavigate();
  const [checking, setChecking] = useState(true);
  const [user, setUser] = useState(null);

  useEffect(() => {
    const token = localStorage.getItem("access_token");

    if (!token) {
      navigate("/login", { replace: true });
      return;
    }

    const verifyToken = async () => {
      try {
        const data = await handleApi("/me", {
          method: "GET",
          headers: { Authorization: `Bearer ${token}` },
        });
        setUser(data);
      } catch {
        localStorage.removeItem("access_token");
        localStorage.removeItem("user");
        navigate("/login", { replace: true });
      } finally {
        setChecking(false);
      }
    };

    verifyToken();
  }, [navigate]);

  if (checking) return <p>Carregando...</p>;

  return (
    <div>
      <div className="title"><h1>Página protegida</h1></div>
      <div className="container">
        <div>
          <span>Seja bem-vindo(a) {user.username}</span>
        </div>
        <div>
          <span>{user.email}</span>
        </div>
      </div>
    </div>
  );
};

export default Home;
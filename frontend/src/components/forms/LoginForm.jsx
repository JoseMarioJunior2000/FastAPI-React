import { useState } from "react";
import { FaUser, FaLock } from "react-icons/fa";
import "../../pages/login/Login.css";
import loginImage from "../../assets/login.svg";

export default function LoginForm({ onSubmit }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  return (
    <div className="login-container">
      <div className="inner">
        <div className="login-image-container">
          <img src={loginImage} alt="Login" className="login-image" />
        </div>

        <form
          onSubmit={(e) => {
            e.preventDefault();
            onSubmit({ email, password });
          }}
          className="login-form"
        >
          <h1>Acesse o sistema</h1>

          <div className="input-group">
            <FaUser className="icon" />
            <input
              type="email"
              placeholder="E-mail"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              autoComplete="email"
              required
            />
          </div>

          <div className="input-group">
            <FaLock className="icon" />
            <input
              type="password"
              placeholder="Senha"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete="current-password"
              required
            />
          </div>

          <div className="recall-forget">
            <label>
              <input type="checkbox" /> Lembre de mim
            </label>
            <a href="#">Esqueceu a senha?</a>
          </div>

          <button type="submit">Entrar</button>

          <div className="signup-link">
            <p>
              Não tem conta? <a href="#">Registrar</a>
            </p>
          </div>
        </form>
      </div>
    </div>
  );
}
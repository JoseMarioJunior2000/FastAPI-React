import { FaUser, FaLock } from 'react-icons/fa';
import { useState } from 'react';
import './Login.css';
import loginImage from '../../assets/login.svg';

function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = (event) => {
    event.preventDefault();
    console.log(username, password);
  };

  return (
    <div className="login-container">
      <div className="login-image-container">
        <img src={loginImage} alt="Login" className="login-image" />
      </div>

      <form onSubmit={handleSubmit} className="login-form">
        <h1>Acesse o sistema</h1>

        <div className="input-group">
          <FaUser className="icon" />
          <input
            type="email"
            placeholder="E-mail"
            onChange={(e) => setUsername(e.target.value)}
          />
        </div>

        <div className="input-group">
          <FaLock className="icon" />
          <input
            type="password"
            placeholder="Senha"
            onChange={(e) => setPassword(e.target.value)}
          />
        </div>

        <div className="recall-forget">
          <label>
            <input type="checkbox" />
            Lembre de mim
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
  );
}

export default Login;

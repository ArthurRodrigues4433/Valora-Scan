import React from 'react'
import './Register.css'
import { FcGoogle } from "react-icons/fc";
import { AiOutlineApple } from "react-icons/ai";
import axios from 'axios'
import { useNavigate } from 'react-router-dom'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const Register = () => {

    const [nome, setNome] = useState('')
    const [email, setEmail] = useState('')
    const [senha, setSenha] = useState('')
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState('')
    const navigate = useNavigate()

    const handleSubmit = async (e) => {
        
    }

    return (
        <div className="container">
            <form action="">
                {/* LOGO */}
                <div className="logo">
                    <div className="icon">
                        <span className="v">V</span>
                        <div className="corner top-left"></div>
                        <div className="corner top-right"></div>
                        <div className="corner bottom-left"></div>
                        <div className="corner bottom-right"></div>
                    </div>
                    <span className="text">
                        <strong>Valora</strong><span className="scan">scan</span>
                    </span>
                </div>

                <div className="logo-header">
                    <h1>Cria conta</h1>
                    <h2>Leva menos de 30 segundos.</h2>
                </div>
                <div>
                    <input type="text" placeholder="Nome" />
                </div>
                <div>
                    <input type="email" placeholder="Email" />
                </div>
                <div>
                    <input type="password" placeholder="Senha" />
                </div>
                <div>
                    <input type="password" placeholder="Confirmar senha" />
                </div>
                <button type="submit" className='button-entry'>Entrar</button>
                <div className="cadastro">
                    Já tem conta? <a className='criarConta' href="/login">Entrar</a>
                </div>
            </form>
        </div>
    )
}
export default Register

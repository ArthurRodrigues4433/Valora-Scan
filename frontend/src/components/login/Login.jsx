import { useState } from 'react'
import './Login.css'
import { FcGoogle } from "react-icons/fc"
import { AiOutlineApple } from "react-icons/ai"
import axios from 'axios'
import { useNavigate } from 'react-router-dom'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const Login = () => {
    const [email, setEmail] = useState('')
    const [senha, setSenha] = useState('')
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState('')
    const navigate = useNavigate()

    const handleSubmit = async (e) => {
        e.preventDefault()
        setLoading(true)
        setError('')

        try {
            const response = await axios.post(`${API_URL}/auth/login`, {
                email,
                senha
            })

            const { access_token, refresh_token } = response.data

            // Armazenar tokens
            localStorage.setItem('access_token', access_token)
            localStorage.setItem('refresh_token', refresh_token)

            // Redirecionar para home
            navigate('/home')
        } catch (err) {
            setError(err.response?.data?.detail || 'Erro ao fazer login')
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="container">
            <form onSubmit={handleSubmit}>
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
                    <h1>Bem-vindo de volta</h1>
                    <h2>Entre para escanear, comprar e economizar</h2>
                </div>

                {error && <div className="error-message">{error}</div>}

                <div>
                    <input
                        type="email"
                        placeholder="Email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        required
                    />
                </div>
                <div>
                    <input
                        type="password"
                        placeholder="Senha"
                        value={senha}
                        onChange={(e) => setSenha(e.target.value)}
                        required
                    />
                </div>
                <button type="submit" className='button-entry' disabled={loading}>
                    {loading ? 'Entrando...' : 'Entrar'}
                </button>
                <div>
                    <a className='esqueceuSenha' href="">Esqueceu sua senha?</a>
                </div>
                <div className="divisor">ou continue com</div>
                <div>
                    <button type="button" className='social-btn-google'>
                        <FcGoogle style={{ marginRight: 8, fontSize: '1.3em', verticalAlign: 'middle' }} />
                        Continuar com Google
                    </button>
                </div>
                <div>
                    <button type="button" className='social-btn-apple'>
                        <AiOutlineApple style={{ marginRight: 8, fontSize: '1.3em', verticalAlign: 'middle' }} />
                        Continuar com Apple
                    </button>
                </div>
                <div className="cadastro">
                    Ainda não tem conta? <a className='criarConta' href="/auth/register">Criar conta</a>
                </div>
            </form>
        </div>
    )
}
export default Login

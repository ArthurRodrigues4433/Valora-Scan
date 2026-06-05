import { useState } from 'react'
import './Register.css'
import axios from 'axios'
import { useNavigate, Link } from 'react-router-dom'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const Register = () => {

    const [nome, setNome] = useState('')
    const [email, setEmail] = useState('')
    const [senha, setSenha] = useState('')
    const [confirmarSenha, setConfirmarSenha] = useState('')
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState('')
    const navigate = useNavigate()

    const handleSubmit = async (e) => {
        e.preventDefault()
        setLoading(true)
        setError('')

        // ← validação antes de enviar
        if (senha !== confirmarSenha) {
            setError('As senhas não coincidem')
            setLoading(false)
            return
        }

        try {
            await axios.post(`${API_URL}/auth/register`, {
                nome,
                email,
                senha,
            })

            navigate('/auth/login')
        } catch (err) {
            setError(err.response?.data?.detail || 'Erro ao registrar')
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
                    <h1>Cria conta</h1>
                    <h2>Leva menos de 30 segundos.</h2>
                </div>

                {error && <div className="error-message">{error}</div>}

                <div>
                    <input type="text" placeholder="Nome" value={nome} onChange={(e) => setNome(e.target.value)} />
                </div>
                <div>
                    <input type="email" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} />
                </div>
                <div>
                    <input type="password" placeholder="Senha" value={senha} onChange={(e) => setSenha(e.target.value)} />
                </div>
                <div>
                    <input type="password" placeholder="Confirmar senha" value={confirmarSenha} onChange={(e) => setConfirmarSenha(e.target.value)} />
                </div>
                <button type="submit" className='button-entry' disabled={loading}>
                    {loading ? 'Criando...' : 'Criar conta'}
                </button>
                <div className="cadastro">
                    Já tem conta? <Link to="/auth/login">Entrar</Link>
                </div>
            </form>
        </div>
    )
}
export default Register

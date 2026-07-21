import { useState, useEffect } from 'react'
import api from '../../services/api'
import { useNavigate } from 'react-router-dom'
import { IoArrowBack, IoPencil, IoLogOut } from 'react-icons/io5'
import './Perfil.css'

const Perfil = () => {
    const [dados, setDados] = useState(null)
    const [loading, setLoading] = useState(true)
    const [editandoNome, setEditandoNome] = useState(false)
    const [novoNome, setNovoNome] = useState('')
    const [salvando, setSalvando] = useState(false)
    const [logoutConfirm, setLogoutConfirm] = useState(false)
    const navigate = useNavigate()

    useEffect(() => {
        const carregarPerfil = async () => {
            try {
                const response = await api.get('/perfil/resumo')
                setDados(response.data)
                setNovoNome(response.data.usuario.nome)
            } catch (error) {
                console.error('Erro ao carregar perfil:', error)
            } finally {
                setLoading(false)
            }
        }
        carregarPerfil()
    }, [])

    const handleSalvarNome = async () => {
        if (!novoNome.trim()) return
        setSalvando(true)
        try {
            await api.put('/perfil/nome', { nome: novoNome })
            setDados(prev => ({ ...prev, usuario: { ...prev.usuario, nome: novoNome } }))
            setEditandoNome(false)
        } catch (error) {
            console.error('Erro ao atualizar nome:', error)
            alert('Erro ao atualizar nome')
        } finally {
            setSalvando(false)
        }
    }

    const handleLogout = () => {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        navigate('/auth/login')
    }

    const formatarMoeda = (valor) => {
        return Number(valor).toFixed(2).replace('.', ',')
    }

    if (loading) {
        return (
            <div className="perfil-container">
                <div className="loading-container">
                    <p>Carregando...</p>
                </div>
            </div>
        )
    }

    if (!dados) {
        return (
            <div className="perfil-container">
                <div className="perfil-empty">
                    <p>Erro ao carregar dados do perfil.</p>
                </div>
            </div>
        )
    }

    const { usuario, estatisticas } = dados

    return (
        <div className="perfil-container">
            <div className="perfil-header">
                <button className="perfil-back-btn" onClick={() => navigate('/home')}>
                    <IoArrowBack />
                </button>

                <div className="perfil-avatar">
                    <span>{usuario.nome.charAt(0).toUpperCase()}</span>
                </div>

                {!editandoNome ? (
                    <div className="perfil-nome-container">
                        <h1 className="perfil-nome">{usuario.nome}</h1>
                        <button className="perfil-edit-btn" onClick={() => setEditandoNome(true)}>
                            <IoPencil />
                        </button>
                    </div>
                ) : (
                    <div className="perfil-edit-form">
                        <input
                            type="text"
                            className="perfil-edit-input"
                            value={novoNome}
                            onChange={(e) => setNovoNome(e.target.value)}
                            autoFocus
                        />
                        <div className="perfil-edit-actions">
                            <button
                                className="perfil-btn-salvar"
                                onClick={handleSalvarNome}
                                disabled={salvando || !novoNome.trim()}
                            >
                                {salvando ? 'Salvando...' : 'Salvar'}
                            </button>
                            <button
                                className="perfil-btn-cancelar"
                                onClick={() => {
                                    setEditandoNome(false)
                                    setNovoNome(usuario.nome)
                                }}
                            >
                                Cancelar
                            </button>
                        </div>
                    </div>
                )}

                <p className="perfil-email">{usuario.email}</p>
            </div>

            <div className="perfil-estatisticas">
                <h2 className="perfil-secao-titulo">Estatisticas</h2>
                <div className="perfil-stats-grid">
                    <div className="perfil-stat-card">
                        <span className="perfil-stat-valor">{estatisticas.total_feiras}</span>
                        <span className="perfil-stat-label">Feiras Criadas</span>
                    </div>
                    <div className="perfil-stat-card">
                        <span className="perfil-stat-valor">{estatisticas.feiras_finalizadas}</span>
                        <span className="perfil-stat-label">Finalizadas</span>
                    </div>
                    <div className="perfil-stat-card">
                        <span className="perfil-stat-valor">{estatisticas.total_itens}</span>
                        <span className="perfil-stat-label">Itens Escaneados</span>
                    </div>
                    <div className="perfil-stat-card destaque">
                        <span className="perfil-stat-valor">R$ {formatarMoeda(estatisticas.total_economia)}</span>
                        <span className="perfil-stat-label">Economia Total</span>
                    </div>
                </div>
            </div>

            <div className="perfil-gasto">
                <div className="perfil-gasto-card">
                    <span className="perfil-gasto-label">Gasto Total em Feiras</span>
                    <span className="perfil-gasto-valor">R$ {formatarMoeda(estatisticas.total_gasto)}</span>
                </div>
            </div>

            <div className="perfil-actions">
                <button className="perfil-action-card">
                    <span className="perfil-action-label">Alterar senha</span>
                    <span className="perfil-action-hint">Em breve</span>
                </button>
            </div>

            <div className="perfil-footer">
                <button className="perfil-logout-btn" onClick={() => setLogoutConfirm(true)}>
                    <IoLogOut />
                    <span>Sair da conta</span>
                </button>
            </div>

            {logoutConfirm && (
                <div className="perfil-modal-overlay">
                    <div className="perfil-modal">
                        <h3>Sair da conta?</h3>
                        <p>Voce sera redirecionado para o login.</p>
                        <div className="perfil-modal-actions">
                            <button className="perfil-btn-cancelar" onClick={() => setLogoutConfirm(false)}>
                                Cancelar
                            </button>
                            <button className="perfil-btn-sair" onClick={handleLogout}>
                                Sair
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    )
}

export default Perfil

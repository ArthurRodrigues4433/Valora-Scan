import { useState, useEffect } from 'react'
import api from '../../services/api'
import './Economia.css'
import BottomNav from "../home/BottomNav/BottomNav";


const Economia = () => {
    const [dados, setDados] = useState(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        const fetchEconomia = async () => {
            try {
                const response = await api.get('/relatorios/economia')
                setDados(response.data)
            } catch (error) {
                console.error('Erro ao carregar economia:', error)
            } finally {
                setLoading(false)
            }
        }
        fetchEconomia()
    }, [])

    if (loading) {
        return (
            <div className="economia-container">
                <div className="loading-container">
                    <p>Carregando...</p>
                </div>
            </div>
        )
    }

    if (!dados) {
        return (
            <div className="economia-container">
                <div className="economia-empty">
                    <p>Erro ao carregar dados de economia.</p>
                </div>
            </div>
        )
    }

    const formatarMoeda = (valor) => {
        return Number(valor).toFixed(2).replace('.', ',')
    }

    const economiaPositiva = dados.economia >= 0

    return (
        <div className="economia-container">
            <div className="economia-header">
                <h1 className="economia-title">Economia do Mês</h1>
                <span className="economia-mes">{dados.mes}</span>
            </div>

            <div className="economia-cards">
                <div className="economia-card">
                    <span className="economia-label">Orçamento</span>
                    <span className="economia-value">R$ {formatarMoeda(dados.orcamento_total)}</span>
                </div>

                <div className="economia-card">
                    <span className="economia-label">Gasto Real</span>
                    <span className="economia-value economia-gasto">R$ {formatarMoeda(dados.gasto_real)}</span>
                </div>

                <div className={`economia-card ${economiaPositiva ? 'economia-destaque-positivo' : 'economia-destaque-negativo'}`}>
                    <span className="economia-label">Economia</span>
                    <span className="economia-value">R$ {formatarMoeda(dados.economia)}</span>
                    <span className="economia-percentual">
                        {dados.percentual_economia}% do orçamento
                    </span>
                </div>

                <div className="economia-card">
                    <span className="economia-label">Itens Escaneados</span>
                    <span className="economia-value">{dados.itens_escaneados || 0}</span>
                </div>
            </div>

            <div className="economia-dica">
                {economiaPositiva ? (
                    <p>Parabéns! Você está economizando este mês. Continue assim!</p>
                ) : (
                    <p>Atenção! Você ultrapassou o orçamento. Tente reduzir gastos desnecessários.</p>
                )}
            </div>
            <BottomNav activeId={3} />
        </div>
    )
}

export default Economia

import { useState, useEffect } from 'react'
import { useNavigate, useParams, useLocation } from 'react-router-dom'
import { IoArrowBack, IoCheckmark, IoPricetag } from 'react-icons/io5'
import api from '../../services/api'
import './Confirmacao.css'

const Confirmacao = () => {
    const { id } = useParams()
    const navigate = useNavigate()
    const location = useLocation()
    
    const [produto, setProduto] = useState({
        nome: '',
        preco_varejo: '',
        preco_atacado: '',
        qtd_minima_atacado: '',
        unidade_medida: '',
        categoria: '',
        imagem_url: ''
    })
    
    const [quantidade, setQuantidade] = useState(1)
    const [ocrTexto, setOcrTexto] = useState('')
    const [confianca, setConfianca] = useState(0)
    const [previewUrl, setPreviewUrl] = useState('')
    const [submitting, setSubmitting] = useState(false)

    useEffect(() => {
        if (!location.state?.produto) {
            navigate(`/feira/${id}`)
            return
        }
        
        const dados = location.state.produto
        setProduto({
            nome: dados.nome || '',
            preco_varejo: dados.preco_varejo?.toString() || '',
            preco_atacado: dados.preco_atacado?.toString() || '',
            qtd_minima_atacado: dados.qtd_minima_atacado?.toString() || '',
            unidade_medida: dados.unidade_medida || '',
            categoria: '',
            imagem_url: location.state.imagemUrl || ''
        })
        setOcrTexto(location.state.ocrTexto || '')
        setConfianca(location.state.confianca || 0)
        setPreviewUrl(location.state.previewUrl || '')
    }, [location.state, navigate, id])

    const precoVarejo = parseFloat(produto.preco_varejo) || 0
    const precoAtacado = parseFloat(produto.preco_atacado) || 0
    const qtdMinima = parseInt(produto.qtd_minima_atacado) || 1
    const precoEscolhido = quantidade >= qtdMinima && precoAtacado > 0 ? precoAtacado : precoVarejo
    const subtotal = quantidade * precoEscolhido
    const tipoPreco = quantidade >= qtdMinima && precoAtacado > 0 ? 'atacado' : 'varejo'

    const handleProdutoChange = (field, value) => {
        setProduto(prev => ({ ...prev, [field]: value }))
    }
    
    const handleBack = () => {
        navigate(`/feira/${id}`)
    }
    
    const handleSubmit = async (e) => {
        e.preventDefault()
        if (!produto.nome || !produto.preco_varejo) {
            alert('Nome e preço varejo são obrigatórios')
            return
        }
        
        setSubmitting(true)
        try {
            await api.post(`/feiras/feira/${id}/itens`, {
                nome: produto.nome,
                categoria: produto.categoria || null,
                preco_varejo: parseFloat(produto.preco_varejo),
                preco_atacado: parseFloat(produto.preco_atacado) || 0,
                qtd_minima_atacado: parseInt(produto.qtd_minima_atacado) || 0,
                quantidade: quantidade,
                unidade_medida: produto.unidade_medida || '',
                imagem_url: produto.imagem_url || null,
                ocr_texto: ocrTexto
            })
            navigate(`/feira/${id}`)
        } catch (error) {
            console.error('Erro ao adicionar item:', error)
            alert('Erro ao adicionar produto à feira')
        } finally {
            setSubmitting(false)
        }
    }
    
    return (
        <div className="confirmacao-container">
            <div className="confirmacao-content">
                <div className="confirmacao-header">
                    <button className="btn-back" onClick={handleBack}>
                        <IoArrowBack />
                    </button>
                    <h2 className="confirmacao-title">Confirmar Produto</h2>
                    {confianca > 0 && (
                        <span className="confianca-badge">
                            {(confianca * 100).toFixed(0)}% confiança
                        </span>
                    )}
                </div>
                
                {previewUrl && (
                    <div className="produto-preview">
                        <img src={previewUrl} alt="Produto" className="preview-image" />
                    </div>
                )}
                
                <form className="confirmacao-form" onSubmit={handleSubmit}>
                    <div className="form-group">
                        <label className="form-label">Nome do Produto</label>
                        <input
                            type="text"
                            className="form-input"
                            value={produto.nome}
                            onChange={e => handleProdutoChange('nome', e.target.value)}
                            placeholder="Digite o nome do produto"
                            required
                        />
                    </div>
                    
                    <div className="form-group">
                        <label className="form-label">Categoria</label>
                        <input
                            type="text"
                            className="form-input"
                            value={produto.categoria}
                            onChange={e => handleProdutoChange('categoria', e.target.value)}
                            placeholder="Ex: Bebidas, Higiene..."
                        />
                    </div>
                    
                    <div className="form-row">
                        <div className="form-group">
                            <label className="form-label">Preço Varejo</label>
                            <input
                                type="number"
                                step="0.01"
                                className="form-input"
                                value={produto.preco_varejo}
                                onChange={e => handleProdutoChange('preco_varejo', e.target.value)}
                                placeholder="0,00"
                                required
                            />
                        </div>
                        
                        <div className="form-group">
                            <label className="form-label">Preço Atacado</label>
                            <input
                                type="number"
                                step="0.01"
                                className="form-input"
                                value={produto.preco_atacado}
                                onChange={e => handleProdutoChange('preco_atacado', e.target.value)}
                                placeholder="0,00"
                            />
                        </div>
                    </div>
                    
                    <div className="form-row">
                        <div className="form-group">
                            <label className="form-label">Qtd. Mínima Atacado</label>
                            <input
                                type="number"
                                className="form-input"
                                value={produto.qtd_minima_atacado}
                                onChange={e => handleProdutoChange('qtd_minima_atacado', e.target.value)}
                                placeholder="Ex: 3"
                            />
                        </div>
                        
                        <div className="form-group">
                            <label className="form-label">Unidade</label>
                            <input
                                type="text"
                                className="form-input"
                                value={produto.unidade_medida}
                                onChange={e => handleProdutoChange('unidade_medida', e.target.value)}
                                placeholder="kg, un, pc..."
                            />
                        </div>
                    </div>
                    
                    <div className="form-group">
                        <label className="form-label">Quantidade</label>
                        <input
                            type="number"
                            min="1"
                            className="form-input"
                            value={quantidade}
                            onChange={e => setQuantidade(parseInt(e.target.value) || 1)}
                        />
                    </div>
                    
                    <div className="preco-resumo">
                        <div className="preco-row">
                            <span className="preco-label">
                                <IoPricetag /> Preço {tipoPreco === 'atacado' ? 'Atacado' : 'Varejo'}
                            </span>
                            <span className="preco-valor">
                                R$ {precoEscolhido.toFixed(2).replace('.', ',')}
                            </span>
                        </div>
                        <div className="preco-row destacado">
                            <span className="preco-label">Subtotal</span>
                            <span className="preco-valor">R$ {subtotal.toFixed(2).replace('.', ',')}</span>
                        </div>
                    </div>
                    
                    <div className="confirmacao-actions">
                        <button
                            type="button"
                            className="btn-cancelar"
                            onClick={handleBack}
                            disabled={submitting}
                        >
                            Cancelar
                        </button>
                        <button
                            type="submit"
                            className="btn-confirmar"
                            disabled={submitting}
                        >
                            <IoCheckmark /> {submitting ? 'Adicionando...' : 'Adicionar à Feira'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    )
}

export default Confirmacao
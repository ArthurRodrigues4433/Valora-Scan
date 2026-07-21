import { useState, useEffect } from "react"
import { useNavigate, useParams, useLocation } from "react-router-dom"
import {
  IoArrowBack,
  IoCheckmarkCircle,
  IoWarning,
  IoRemoveCircle,
  IoAddCircle,
} from "react-icons/io5"
import api from "../../services/api"
import "./Comparacao.css"

const Comparacao = () => {
  const { id } = useParams()
  const navigate = useNavigate()
  const location = useLocation()

  const [comparacao, setComparacao] = useState(null)
  const [loading, setLoading] = useState(true)
  const [confirming, setConfirming] = useState(false)

  useEffect(() => {
    const data = location.state?.comparacao

    if (data) {
      setComparacao(data)
      setLoading(false)
    } else {
      fetchComparacao()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [location.state, id])

  const fetchComparacao = async () => {
    try {
      // Ajuste este endpoint conforme sua API real
      const response = await api.get(`/nfce/divergencias/${id}`)
      setComparacao(response.data)
    } catch (error) {
      console.error("Erro ao buscar comparação:", error)
      alert(error.response?.data?.detail || "Erro ao carregar comparação")
    } finally {
      setLoading(false)
    }
  }

  const handleConfirmar = async () => {
    setConfirming(true)
    try {
      // Ajuste este endpoint conforme sua API real
      await api.post(`/feiras/feira/${id}/finalizar`)
      navigate("/feiras", { replace: true })
    } catch (error) {
      console.error("Erro ao confirmar:", error)
      alert(error.response?.data?.detail || "Erro ao confirmar compra")
    } finally {
      setConfirming(false)
    }
  }

  const handleBack = () => {
    navigate("/feira", { replace: true })
  }

  if (loading) {
    return (
      <div className="comparacao-container">
        <div className="comparacao-loading">
          <div className="spinner"></div>
          <p>Carregando comparação...</p>
        </div>
      </div>
    )
  }

  if (!comparacao) {
    return (
      <div className="comparacao-container">
        <div className="comparacao-empty">
          <p>Nenhuma comparação disponível</p>
          <button className="btn-voltar" onClick={handleBack}>
            Voltar
          </button>
        </div>
      </div>
    )
  }

  const comp = comparacao?.comparacao || comparacao || {}
  const listaItens = comp.itens || []
  const resumo = comp.resumo || {}

  const itensOk = listaItens.filter((i) => !i.divergente)
  const itensDivergentes = listaItens.filter((i) => i.divergente)
  const naoEncontrados = resumo.nao_encontrados || []
  const adicionais = resumo.adicionais || []
  const totalDivergencias = itensDivergentes.length

  return (
    <div className="comparacao-container">
      <div className="comparacao-header">
        <button className="btn-back" onClick={handleBack}>
          <IoArrowBack />
        </button>
        <div className="comparacao-header-info">
          <h2>Resultado da Compra</h2>
          <span className="comparacao-subtitle">
            {(comp.mercado || comparacao.mercado || "Mercado") +
              " • " +
              (comp.data_compra || comparacao.data_compra || "")}
          </span>
        </div>
      </div>

      <div className="comparacao-resumo-cards">
        <div className="resumo-card ok">
          <span className="resumo-valor">{itensOk.length}</span>
          <span className="resumo-label">Conferidos</span>
        </div>
        <div className="resumo-card divergencia">
          <span className="resumo-valor">{totalDivergencias}</span>
          <span className="resumo-label">Divergências</span>
        </div>
        <div className="resumo-card nao-encontrado">
          <span className="resumo-valor">{naoEncontrados.length}</span>
          <span className="resumo-label">Na Lista, Não na Nota</span>
        </div>
        <div className="resumo-card adicional">
          <span className="resumo-valor">{adicionais.length}</span>
          <span className="resumo-label">Na Nota, Não na Lista</span>
        </div>
      </div>

      <div className="comparacao-totais">
        <div className="total-item economia">
          <span className="total-label">Economia</span>
          <span className="total-valor">
            R$ {(comp.economia || 0).toFixed(2).replace(".", ",")}
          </span>
        </div>
        <div className="total-item prejuizo">
          <span className="total-label">Prejuízo</span>
          <span className="total-valor">
            R$ {(comp.prejuizo || 0).toFixed(2).replace(".", ",")}
          </span>
        </div>
      </div>

      <div className="comparacao-sections">
        {itensOk.length > 0 && (
          <div className="comparacao-section">
            <h3 className="section-title ok">
              <IoCheckmarkCircle /> Itens Conferidos ({itensOk.length})
            </h3>
            <div className="comparacao-lista">
              {itensOk.map((item) => (
                <div key={item.id} className="comparacao-item ok">
                  <div className="item-nome">
                    <IoCheckmarkCircle color="#2f8d3f" />
                    <span>{item.nome}</span>
                  </div>
                  <div className="item-precos">
                    <span className="preco-esperado">
                      Lista: R${" "}
                      {(item.preco_esperado || 0).toFixed(2).replace(".", ",")}
                    </span>
                    <span className="preco-encontrado">
                      Nota: R${" "}
                      {(item.preco_encontrado || 0).toFixed(2).replace(".", ",")}
                    </span>
                  </div>
                  <div className="item-detalhes">
                    Qtd: {item.quantidade} | Subtotal: R${" "}
                    {(item.quantidade * (item.preco_encontrado || 0))
                      .toFixed(2)
                      .replace(".", ",")}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {totalDivergencias > 0 && (
          <div className="comparacao-section">
            <h3 className="section-title divergencia">
              <IoWarning /> Divergências de Preço ({totalDivergencias})
            </h3>
            <div className="comparacao-lista">
              {itensDivergentes.map((item) => (
                <div key={item.id} className="comparacao-item divergente">
                  <div className="item-nome">
                    <IoWarning color="#e74c3c" />
                    <span>{item.nome}</span>
                  </div>
                  <div className="item-precos">
                    <span className="preco-esperado">
                      Lista: R${" "}
                      {(item.preco_esperado || 0).toFixed(2).replace(".", ",")}
                    </span>
                    <span className="preco-encontrado">
                      Nota: R${" "}
                      {(item.preco_encontrado || 0).toFixed(2).replace(".", ",")}
                    </span>
                  </div>
                  <div className="item-diferenca">
                    {item.diferenca > 0 ? "+" : ""}
                    R$ {Math.abs(item.diferenca || 0).toFixed(2).replace(".", ",")}
                    {item.diferenca > 0 ? " mais caro" : " mais barato"}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {naoEncontrados.length > 0 && (
          <div className="comparacao-section">
            <h3 className="section-title nao-encontrado">
              <IoRemoveCircle /> Na Lista mas Não Na Nota ({naoEncontrados.length})
            </h3>
            <div className="comparacao-lista">
              {naoEncontrados.map((item) => (
                <div
                  key={item.item_feira_id}
                  className="comparacao-item nao-encontrado"
                >
                  <div className="item-nome">
                    <IoRemoveCircle color="#e67e22" />
                    <span>{item.nome}</span>
                  </div>
                  <div className="item-detalhes">
                    Qtd: {item.quantidade} | Preço lista: R${" "}
                    {(item.preco || 0).toFixed(2).replace(".", ",")}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {adicionais.length > 0 && (
          <div className="comparacao-section">
            <h3 className="section-title adicional">
              <IoAddCircle /> Na Nota mas Não Na Lista ({adicionais.length})
            </h3>
            <div className="comparacao-lista">
              {adicionais.map((item) => (
                <div key={item.item_nota_id} className="comparacao-item adicional">
                  <div className="item-nome">
                    <IoAddCircle color="#3498db" />
                    <span>{item.nome}</span>
                  </div>
                  <div className="item-detalhes">
                    Qtd: {item.quantidade} | Preço nota: R${" "}
                    {(item.preco || 0).toFixed(2).replace(".", ",")}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      <div className="comparacao-footer">
        <button
          className="btn-confirmar-comparacao"
          onClick={handleConfirmar}
          disabled={confirming}
        >
          {confirming ? "Confirmando..." : "Confirmar e Finalizar Compra"}
        </button>
      </div>
    </div>
  )
}

export default Comparacao

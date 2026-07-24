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
  const [filtro, setFiltro] = useState("comparacao")

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
          <button className="btn-voltar" onClick={handleBack} aria-label="Voltar">
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

  const agruparItens = (itens, tipo) => {
    const grupos = new Map()

    itens.forEach((item) => {
      const precoListaBase =
        tipo === "nao-nota"
          ? 0
          : item.preco_esperado || item.preco || 0
      const precoNotaBase =
        tipo === "nao-lista"
          ? 0
          : item.preco_encontrado || item.preco || 0
      const chave =
        item.ean ||
        item.cod_interno ||
        `${item.nome}|${precoListaBase}|${precoNotaBase}`

      if (!grupos.has(chave)) {
        grupos.set(chave, {
          id: item.id,
          nome: item.nome,
          preco_esperado: precoListaBase,
          preco_encontrado: precoNotaBase,
          tipo,
          quantidade: 0,
          precoListaTotal: 0,
          precoNotaTotal: 0,
          diferencaTotal: 0,
        })
      }

      const grupo = grupos.get(chave)
      const qtd = item.quantidade || 1
      grupo.quantidade += qtd
      grupo.precoListaTotal += precoListaBase * qtd
      grupo.precoNotaTotal += precoNotaBase * qtd
      grupo.diferencaTotal += (item.diferenca || 0) * qtd
    })

    return Array.from(grupos.values()).map((grupo) => {
      const diff = grupo.diferencaTotal || 0
      const listaMaior = grupo.preco_esperado > grupo.preco_encontrado
      const diffAbs = Math.abs(diff).toFixed(2).replace(".", ",")
      const base = {
        id: grupo.id,
        nome: grupo.nome,
        tipo: grupo.tipo,
        precoLista:
          grupo.tipo === "nao-nota"
            ? "—"
            : `R$ ${grupo.precoListaTotal.toFixed(2).replace(".", ",")}`,
        precoNota:
          grupo.tipo === "nao-lista"
            ? "—"
            : `R$ ${grupo.precoNotaTotal.toFixed(2).replace(".", ",")}`,
        diferenca:
          grupo.tipo === "ok"
            ? "—"
            : grupo.tipo === "nao-lista"
            ? "Só na lista"
            : grupo.tipo === "nao-nota"
            ? "Só na nota"
            : listaMaior
            ? `-R$ ${diffAbs}`
            : `+R$ ${diffAbs}`,
      }

      if (grupo.tipo === "ok") {
        return { ...base, precoListaCor: "", precoNotaCor: "", diferencaCor: "igual" }
      }

      if (grupo.tipo === "divergencia") {
        return {
          ...base,
          precoListaCor: listaMaior ? "preco-prejuizo" : "preco-economia",
          precoNotaCor: listaMaior ? "preco-economia" : "preco-prejuizo",
          diferencaCor: listaMaior ? "diferenca-economia" : "diferenca-prejuizo",
        }
      }

      if (grupo.tipo === "nao-lista") {
        return { ...base, diferencaCor: "somente-lista" }
      }

      if (grupo.tipo === "nao-nota") {
        return { ...base, diferencaCor: "somente-nota" }
      }

      return base
    })
  }

  const itensOkAgrupados = agruparItens(itensOk, "ok")
  const itensDivergentesAgrupados = agruparItens(itensDivergentes, "divergencia")
  const naoEncontradosAgrupados = agruparItens(naoEncontrados, "nao-lista")
  const adicionaisAgrupados = agruparItens(adicionais, "nao-nota")

  const itensTabela = [
    ...itensOkAgrupados,
    ...itensDivergentesAgrupados,
    ...naoEncontradosAgrupados,
    ...adicionaisAgrupados,
  ]

  const totalDivergencias = itensDivergentesAgrupados.length

  const itensFiltrados =
    filtro === "comparacao"
      ? itensTabela
      : itensTabela.filter((item) => {
          if (filtro === "divergencias") return item.tipo === "divergencia"
          if (filtro === "lista") return item.tipo === "nao-lista"
          if (filtro === "nota") return item.tipo === "nao-nota"
          return true
        })

  return (
    <div className="comparacao-container">
      <div className="comparacao-header">
        <button className="btn-back" onClick={handleBack} aria-label="Voltar">
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

      <div className="comparacao-filter-tabs">
        <button
          className={`filter-tab ${filtro === "comparacao" ? "active" : ""}`}
          onClick={() => setFiltro("comparacao")}
        >
          🟢 Comparação
        </button>
        <button
          className={`filter-tab ${filtro === "divergencias" ? "active" : ""}`}
          onClick={() => setFiltro("divergencias")}
        >
          Divergências
        </button>
        <button
          className={`filter-tab ${filtro === "lista" ? "active" : ""}`}
          onClick={() => setFiltro("lista")}
        >
          Só na lista
        </button>
        <button
          className={`filter-tab ${filtro === "nota" ? "active" : ""}`}
          onClick={() => setFiltro("nota")}
        >
          Só na nota
        </button>
      </div>

      <div className="comparacao-tabela-wrapper">
        <div className="comparacao-tabela">
          <div className="tabela-header">
            <div className="col-item">Item</div>
            <div className="col-lista">Lista</div>
            <div className="col-nota">Nota</div>
            <div className="col-diferenca">Diferença</div>
          </div>
          {itensFiltrados.map((item) => (
            <div key={item.id} className={`tabela-linha ${item.tipo}`}>
              <div className="col-item">
                <span className={`linha-indicador ${item.tipo}`}></span>
                <span className="item-nome-text">{item.nome}</span>
              </div>
              <div className={`col-lista ${item.tipo === "ok" ? "preco-ok" : item.tipo === "divergencia" ? item.precoListaCor : ""}`}>
                {item.precoLista}
              </div>
              <div className={`col-nota ${item.tipo === "ok" ? "preco-ok" : item.tipo === "divergencia" ? item.precoNotaCor : ""}`}>
                {item.precoNota}
              </div>
              <div className={`col-diferenca ${item.tipo === "ok" ? "igual" : item.tipo === "nao-lista" ? "somente-lista" : item.tipo === "nao-nota" ? "somente-nota" : item.diferencaCor}`}>
                {item.diferenca}
              </div>
            </div>
          ))}
          {itensFiltrados.length === 0 && (
            <div className="tabela-vazia">
              Nenhum item encontrado para este filtro.
            </div>
          )}
        </div>
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

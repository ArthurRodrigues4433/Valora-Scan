import { useParams, useNavigate } from "react-router-dom";
import { useState, useEffect, useRef } from "react";
import "./FeiraDetalhe.css";
import { IoScan, IoArrowBack } from "react-icons/io5";
import api from "../../../services/api";

const STATUS_CONFIG = {
    em_andamento: { label: "Em andamento", color: "#e6a817", bg: "rgba(230, 168, 23, 0.1)" },
    andamento: { label: "Em andamento", color: "#e6a817", bg: "rgba(230, 168, 23, 0.1)" },
    finalizada: { label: "Finalizada", color: "#e74c3c", bg: "rgba(231, 76, 60, 0.1)" },
    cancelada: { label: "Cancelada", color: "#e74c3c", bg: "rgba(231, 76, 60, 0.1)" },
    pausada: { label: "Pausada", color: "#e6a817", bg: "rgba(230, 168, 23, 0.1)" },
};

const FeiraDetalhe = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const [feira, setFeira] = useState(null);
    const [loading, setLoading] = useState(true);
    const [showItemModal, setShowItemModal] = useState(false);
    const [itemSelecionado, setItemSelecionado] = useState(null);
    const [quantidadeModal, setQuantidadeModal] = useState(0);
    const [savingItem, setSavingItem] = useState(false);
    const [buscaItem, setBuscaItem] = useState("");
    const buscaRef = useRef(null);
    const modalBoxRef = useRef(null);

    useEffect(() => {
        if (showItemModal && modalBoxRef.current) {
            modalBoxRef.current.scrollTop = 0;
        }
    }, [showItemModal]);

    const openItemModal = (item) => {
        setItemSelecionado(item);
        setQuantidadeModal(item.quantidade || 1);
        setShowItemModal(true);
    };

    const closeItemModal = () => {
        setShowItemModal(false);
        setItemSelecionado(null);
        setQuantidadeModal(0);
        setSavingItem(false);
    };

    const handleSaveQuantidade = async () => {
        if (!itemSelecionado || !feira) return;
        setSavingItem(true);
        try {
            await api.patch(`/feiras/feira/${feira.id}/itens/${itemSelecionado.id}`, {
                quantidade: quantidadeModal,
            });
            await fetchFeira();
            closeItemModal();
        } catch (error) {
            alert(error.response?.data?.detail || "Erro ao atualizar quantidade");
        } finally {
            setSavingItem(false);
        }
    };

    const handleDeleteItem = async () => {
        if (!itemSelecionado || !feira) return;
        const confirmou = window.confirm(`Deseja realmente apagar "${itemSelecionado.nome}"?`);
        if (!confirmou) return;
        setSavingItem(true);
        try {
            await api.delete(`/feiras/feira/${feira.id}/itens/${itemSelecionado.id}`);
            await fetchFeira();
            closeItemModal();
        } catch (error) {
            alert(error.response?.data?.detail || "Erro ao apagar item");
        } finally {
            setSavingItem(false);
        }
    };

    const fetchFeira = async () => {
        setLoading(true);

        try {
            const response = await api.get(`/feiras/feira/${id}`);
            setFeira(response.data);

        } catch (error) {
            console.error("Erro ao carregar feira:", error);

            if (error.response?.status === 404) {
                alert("Feira não encontrada.");
                navigate("/feiras", { replace: true });
                return;
            }

            if (error.response?.status === 403) {
                alert("Você não tem permissão para acessar essa feira.");
                navigate("/feiras", { replace: true });
                return;
            }

            alert("Erro ao carregar a feira.");
            navigate("/feiras", { replace: true });

        } finally {
            setLoading(false);
        }
    };

    const handleBack = () => {
        navigate("/feiras", { replace: true });
    };

    const handleScanProduct = () => {
        navigate(`/feira/${id}/scan`);
    };

    const handleScanNFCe = () => {
        navigate(`/feira/${id}/scan-nfce`);
    };

    useEffect(() => {
        fetchFeira();
    }, [id]);

    if (!feira) {
        return null;
    }

    const feiraData = feira;
    const gastoParcial = (feiraData.itens || []).reduce((total, item) => total + (item.subtotal || 0), 0);
    const economiaParcial = (feiraData.itens || [])
        .filter(item => item.preco_escolhido === item.preco_atacado && item.preco_atacado)
        .reduce((total, item) => total + ((item.quantidade || 0) * ((item.preco_varejo || 0) - (item.preco_atacado || 0))), 0);
    const getStatusConfig = (status) =>
        STATUS_CONFIG[status] || {
            label: "Desconhecido",
            color: "#6b7280",
            bg: "#f3f4f6",
        };

    return (
        <div className="feira-detalhe-container">
            {loading ? (
                <div className="loading-container">
                    <p>Carregando...</p>
                </div>
            ) : (
                <div className="feira-detalhe-content">
                    <div className="feira-detalhe-header">
                        <button className="btn-back" onClick={handleBack}>
                            <IoArrowBack />
                        </button>
                        <h2 className="feira-detalhe-title">{feiraData.nome}</h2>
                        <span
                            className="feira-status"
                            style={{ color: getStatusConfig(feiraData.status).color, backgroundColor: getStatusConfig(feiraData.status).bg }}
                        >
                            {getStatusConfig(feiraData.status).label}
                        </span>
                    </div>

                    <div className="feira-detalhe-info">
                        <div className="info-row">
                            <span className="info-label">Data</span>
                            <span className="info-value">{feiraData.data}</span>
                        </div>
                        <div className="info-row">
                            <span className="info-label">Itens scaneados</span>
                            <span className="info-value">{feiraData.itensScaneados}</span>
                        </div>
                        <div className="info-row">
                            <span className="info-label">Valor total da feira</span>
                            <span className="info-value">R$ {(feiraData.gasto_total || 0).toFixed(2).replace('.', ',')}</span>
                        </div>
                        <div className="info-row">
                            <span className="info-label">Gasto parcial</span>
                            <span className="info-value">R$ {gastoParcial.toFixed(2).replace('.', ',')}</span>
                        </div>
                        <div className="info-row">
                            <span className="info-label">Economia parcial</span>
                            <span className="info-value">R$ {economiaParcial.toFixed(2).replace('.', ',')}</span>
                        </div>
                    </div>

                    <button className="btn-scan-novo" onClick={handleScanProduct}>
                        <IoScan /> Escanear novo produto
                    </button>

                    {(feiraData.status === "em_andamento" || feiraData.status === "pausada" || feiraData.status === "andamento") && feiraData.itens && feiraData.itens.length > 0 && (
                        <button className="btn-scan-nfce" onClick={handleScanNFCe}>
                            <IoScan /> Escanear NFCe da nota
                        </button>
                    )}

                    <div className="itens-section">
                        <h3 className="itens-title">Todos os Itens</h3>
                        <div className="busca-item-wrapper">
                            <input
                                ref={buscaRef}
                                type="text"
                                className="busca-item-input"
                                placeholder="Buscar item pelo nome..."
                                value={buscaItem}
                                onChange={(e) => setBuscaItem(e.target.value)}
                                onFocus={() => buscaRef.current?.scrollIntoView({ behavior: "smooth", block: "center" })}
                            />
                        </div>
                        {(feiraData.itens && feiraData.itens.length > 0) ? (
                            <div className="itens-list">
                                {feiraData.itens
                                    .filter((item) =>
                                        (item.nome || "").toLowerCase().includes(buscaItem.trim().toLowerCase())
                                    )
                                    .map((item) => {
                                    const economia = item.preco_atacado && item.preco_escolhido === item.preco_atacado
                                        ? (item.preco_varejo - item.preco_atacado) * item.quantidade
                                        : 0;
                                    const deixou_economia = item.preco_atacado && item.preco_escolhido === item.preco_varejo && item.preco_atacado !== item.preco_varejo
                                        ? (item.preco_varejo - item.preco_atacado) * item.quantidade
                                        : 0;
                                    return (
                                        <ItemCard
                                            key={item.id}
                                            nome={item.nome}
                                            preco={item.preco_escolhido}
                                            precoVarejo={item.preco_varejo}
                                            precoAtacado={item.preco_atacado}
                                            quantidade={item.quantidade}
                                            tipo={item.tipo}
                                            unidade_medida={item.unidade_medida}
                                            economia={economia}
                                            deixou_economia={deixou_economia}
                                            onClick={() => openItemModal(item)}
                                        />
                                    );
                                })}
                            </div>
                        ) : (
                            <div className="itens-empty">
                                <div className="empty-icon">
                                    <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                                        <path d="M3 3h18v18H3zM3 9h18M9 21V9" />
                                    </svg>
                                </div>
                                <h4>Nenhum item adicionado</h4>
                                <p>Toque em "Escanear novo produto" para adicionar itens à sua feira</p>
                            </div>
                        )}
                    </div>
                </div>
            )}

            {showItemModal && (
                <div className="modal-overlay" onClick={closeItemModal}>
                    <div className="modal-box" ref={modalBoxRef} onClick={(e) => e.stopPropagation()}>
                        <h3>Alterar item</h3>
                        <div className="modal-field">
                            <label>Item</label>
                            <input
                                type="text"
                                value={itemSelecionado?.nome || ""}
                                disabled
                                style={{ opacity: 0.7 }}
                                onFocus={(e) => e.target.scrollIntoView({ behavior: "smooth", block: "center" })}
                            />
                        </div>
                        <div className="modal-field">
                            <label>Quantidade</label>
                            <input
                                type="number"
                                value={quantidadeModal}
                                onChange={(e) => setQuantidadeModal(Number(e.target.value))}
                                min="0"
                                step="1"
                                onFocus={(e) => e.target.scrollIntoView({ behavior: "smooth", block: "center" })}
                            />
                        </div>
                        <div className="modal-actions">
                            <button className="btn-deletar" onClick={handleDeleteItem} disabled={savingItem}>
                                Apagar
                            </button>
                            <button className="btn-cancelar" onClick={closeItemModal} disabled={savingItem}>
                                Cancelar
                            </button>
                            <button className="btn-criar" onClick={handleSaveQuantidade} disabled={savingItem}>
                                {savingItem ? "Salvando..." : "Salvar"}
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

const ItemCard = ({ nome, preco, precoVarejo, precoAtacado, quantidade, unidade_medida, economia, deixou_economia, onClick }) => {

    function saberTipoAtacadoVarejo(valorUnitario, precoAtacado, precoVarejo) {
        if (valorUnitario === precoAtacado) return "atacado";
        if (valorUnitario === precoVarejo) return "varejo";
        return null;
    }

    const tipoConfig = {
        atacado: { label: "Atacado", bg: "#2f8d3f", color: "#fff" },
        varejo: { label: "Varejo", bg: "#3498db", color: "#fff" },
    };
    const tipoItem = saberTipoAtacadoVarejo(preco, precoAtacado, precoVarejo);

    return (
        <div className="card-item" onClick={onClick} style={{ cursor: "pointer" }}>
            <div className="item-info">
                <div className="icone-item">{(nome || "?").charAt(0)}</div>
                <div>
                    <h4>{nome}</h4>
                    <div className="item-tipo">
                        <span style={{ backgroundColor: tipoConfig[tipoItem]?.bg, color: tipoConfig[tipoItem]?.color, marginRight: 6 }}>
                            {tipoConfig[tipoItem]?.label}
                        </span>
                        <span className="item-quantidade">{quantidade} {unidade_medida || ""}</span>
                    </div>
                    <div className="item-meta">
                        {economia > 0 && (
                            <span className="item-economia">↗ Economizou R$ {economia.toFixed(2).replace('.', ',')}</span>
                        )}
                        {deixou_economia > 0 && (
                            <span className="item-perdeu">↘ Poderia economizar {deixou_economia.toFixed(2).replace('.', ',')}</span>
                        )}
                    </div>
                    <div className="item-preco-unidade">
                        {precoAtacado && precoAtacado > 0 ? (
                            preco === precoAtacado ? (
                                <>R$ {preco.toFixed(2).replace('.', ',')}/un • De R$ {precoVarejo.toFixed(2).replace('.', ',')}</>
                            ) : (
                                <>
                                    R$ {preco.toFixed(2).replace('.', ',')}/un • <span style={{ color: '#3B82f6' }}>Atacado: R$ {precoAtacado.toFixed(2).replace('.', ',')}</span>
                                </>
                            )
                        ) : (
                            <>R$ {preco.toFixed(2).replace('.', ',')}/un</>
                        )}
                    </div>
                </div>
            </div>
            <div className="item-preco">
                <strong>R$ {(preco * quantidade).toFixed(2).replace('.', ',')}</strong>
            </div>
        </div>
    );
};

export default FeiraDetalhe;
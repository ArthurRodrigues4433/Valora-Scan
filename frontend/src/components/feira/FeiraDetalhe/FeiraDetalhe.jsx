import { useParams, useNavigate } from "react-router-dom";
import { useState, useEffect } from "react";
import "./FeiraDetalhe.css";
import { IoScan, IoArrowBack, IoCheckmarkCircle } from "react-icons/io5";
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
    const [finalizing, setFinalizing] = useState(false);

    const fetchFeira = async () => {
        try {
            const response = await api.get(`/feiras/feira/${id}`);
            setFeira(response.data);
        } catch (error) {
            console.error("Erro ao carregar feira:", error);
            alert("Erro ao carregar os dados da feira");
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

    const handleFinalizar = async () => {
        if (window.confirm("Deseja realmente finalizar esta feira?")) {
            setFinalizing(true);
            try {
                await api.put(`/feiras/feira/${id}`, { status: "finalizada" });
                setFeira(prev => ({ ...prev, status: "finalizada" }));
            } catch (error) {
                console.error("Erro ao finalizar feira:", error);
                alert("Erro ao finalizar feira");
            } finally {
                setFinalizing(false);
            }
        }
    };

    useEffect(() => {
        fetchFeira();
    }, [id]);

    const feiraData = feira || {};
    const gastoParcial = (feiraData.itens || []).reduce((total, item) => total + (item.subtotal || 0), 0);
    const economiaParcial = (feiraData.itens || [])
        .filter(item => item.tipo === "atacado" && item.preco_atacado)
        .reduce((total, item) => total + ((item.quantidade || 0) * ((item.preco_varejo || 0) - (item.preco_atacado || 0))), 0);
    const getStatusConfig = (status) =>
        STATUS_CONFIG[status] || STATUS_CONFIG.finalizada;

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

                    <div className="itens-section">
                        <h3 className="itens-title">Itens da feira</h3>
                        {(feiraData.itens && feiraData.itens.length > 0) ? (
                            <div className="itens-list">
                                {feiraData.itens.map((item) => (
                                    <ItemCard
                                        key={item.id}
                                        nome={item.nome}
                                        preco={item.preco_escolhido}
                                        precoVarejo={item.preco_varejo}
                                        precoAtacado={item.preco_atacado}
                                        quantidade={item.quantidade}
                                        tipo={item.tipo}
                                        unidade={item.unidade_medida}
                                        valorUnitario={item.preco_escolhido}
                                    />
                                ))}
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

            {(feiraData.status === "em_andamento" || feiraData.status === "pausada") && (
                <div className="feira-detalhe-footer">
                    <button className="btn-finalizar-fixed" onClick={handleFinalizar} disabled={finalizing}>
                        <IoCheckmarkCircle /> {finalizing ? "Finalizando..." : "Finalizar feira"}
                    </button>
                </div>
            )}
        </div>
    );
};

const ItemCard = ({ nome, preco, precoVarejo, precoAtacado, quantidade, tipo, unidade, economia, valorUnitario }) => {

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
    const valorTotal = preco * quantidade;

    return (
        <div className="card-item">
            <div className="item-info">
                <div className="icone-item"></div>
                <div>
                    <h4>{nome}</h4>
                    <div className="item-tipo">
                        <span style={{ backgroundColor: tipoConfig[tipoItem].bg, color: tipoConfig[tipoItem].color, marginRight: 6 }}>
                            {tipoConfig[tipoItem].label}
                        </span>
                        <span className="item-quantidade">{quantidade} un</span>
                    </div>
                    <div className="item-meta">
                        {economia > 0 && (
                            <span className="item-economia">🟢 Economizou R$ {economia.toFixed(2).replace('.', ',')}</span>
                        )}
                    </div>
                    <div className="item-preco-unidade">
                        R$ {valorUnitario.toFixed(2).replace('.', ',')}/un • De R$ {precoVarejo.toFixed(2).replace('.', ',')}
                    </div>
                </div>
            </div>
            <div className="item-preco">
                <strong>R$ {valorTotal.toFixed(2).replace('.', ',')}</strong>
            </div>
        </div>
    );
};

export default FeiraDetalhe;
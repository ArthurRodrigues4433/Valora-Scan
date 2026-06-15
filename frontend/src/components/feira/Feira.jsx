import { useState, useEffect } from "react";
import "./Feira.css";
import { IoAdd, IoTrashOutline } from "react-icons/io5";
import { useNavigate } from "react-router-dom";
import api from "../../services/api";

const STATUS_CONFIG = {
    em_andamento: { label: "Em andamento", color: "#e6a817", bg: "rgba(230, 168, 23, 0.1)" },
    andamento: { label: "Em andamento", color: "#e6a817", bg: "rgba(230, 168, 23, 0.1)" },
    finalizada: { label: "Finalizada", color: "#e74c3c", bg: "rgba(231, 76, 60, 0.1)" },
    cancelada: { label: "Cancelada", color: "#e74c3c", bg: "rgba(231, 76, 60, 0.1)" },
    pausada: { label: "Pausada", color: "#e6a817", bg: "rgba(230, 168, 23, 0.1)" },
};

const FeiraCardItem = ({ feira, onClick, onDelete }) => {
    const status = STATUS_CONFIG[feira.status] || STATUS_CONFIG.finalizada;
    return (
        <div className="card-feira" key={feira.id} onClick={() => onClick(feira.id)}>
            <div className="linha-topo">
                <div>
                    <h4>{feira.nome}</h4>
                    <small>{feira.data}</small>
                </div>
                <div className="card-actions">
                    <button
                        className="btn-deletar-feira"
                        onClick={(event) => onDelete(event, feira.id, feira.nome)}
                        title="Deletar feira"
                    >
                        <IoTrashOutline />
                    </button>
                    <span
                        className="feira-status"
                        style={{ color: status.color, backgroundColor: status.bg }}
                    >
                        {status.label}
                    </span>
                </div>
            </div>
            <div className="linha-valores">
                <span>Gasto</span>
                <span>{`R$ ${feira.gasto_atual.toFixed(2).replace('.', ',')} / R$ ${feira.gasto_total.toFixed(2).replace('.', ',')}`}</span>
            </div>
            <div className="feira-header-valores">
                <span className="economia-label">Economia</span>
                <strong className="economia-value">{`R$ ${feira.economia.toFixed(2).replace('.', ',')}`}</strong>
            </div>
        </div>
    );
};

const Feira = () => {
    const [feiras, setFeiras] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showModal, setShowModal] = useState(false);
    const [nome, setNome] = useState("");
    const [orcamento, setOrcamento] = useState("");
    const [saving, setSaving] = useState(false);
    const navigate = useNavigate();

    const fetchFeiras = async () => {
        try {
            const response = await api.get("/feiras/feira/resumo");
            setFeiras(response.data);
        } catch (error) {
            console.warn("API indisponível, exibindo estado vazio:", error.message);
            setFeiras([]);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchFeiras();
    }, []);

    const handleCreate = async () => {
        if (!nome.trim() || !orcamento) return;
        setSaving(true);
        try {
            await api.post("/feiras/feira", {
                nome: nome.trim(),
                orcamento: parseFloat(orcamento),
            });
            setShowModal(false);
            setNome("");
            setOrcamento("");
            await fetchFeiras();
            navigate(`/home#feira}`);
        } catch (error) {
            console.error("Erro ao criar feira:", error);
            alert(error.response?.data?.detail || "Erro ao criar feira");
        } finally {
            setSaving(false);
        }
    };

    const handleCancel = () => {
        setShowModal(false);
        setNome("");
        setOrcamento("");
    };
    
    const handleDelete = async (event, id, nome) => {
        event.stopPropagation();

        const confirmou = window.confirm(`Deseja realmente deletar a feira "${nome}"?`);
        if (!confirmou) return;

        try {
            await api.delete(`/feiras/feira/${id}`);
            await fetchFeiras();
        } catch (error) {
            console.error("Erro ao deletar feira:", error);
            alert(error.response?.data?.detail || "Erro ao deletar feira");
        }
    };

    if (loading) {
        return (
            <div className="feira-container">
                <div className="feira-header">
                    <h2 className="feira-title">Minhas Feiras</h2>
                    <button className="btn-nova-feira" onClick={() => setShowModal(true)}>
                        <IoAdd /> Nova feira
                    </button>
                </div>
                <div className="loading-state">
                    <div className="spinner"></div>
                </div>
            </div>
        );
    }

    const hasActiveFeira = feiras.some(
        (f) => f.status === "em_andamento" || f.status === "andamento" || f.status === "pausada"
    );

    return (
        <div className="feira-container">
            <div className="feira-header">
                <h2 className="feira-title">Minhas Feiras</h2>
                <button
                    className="btn-nova-feira"
                    onClick={() => setShowModal(true)}
                    disabled={hasActiveFeira}
                    title={
                        hasActiveFeira
                            ? "Finalize ou cancele a feira atual antes de criar uma nova"
                            : ""
                    }
                >
                    <IoAdd /> Nova feira
                </button>
            </div>
            {hasActiveFeira && (
                <p className="feira-header-alert">
                    Finalize ou cancele a feira atual antes de criar uma nova
                </p>
            )}

            {feiras.length === 0 ? (
                <div className="feira-empty">
                    <div className="empty-icon">
                        <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                            <path d="M3 3h18v18H3zM3 9h18M9 21V9" />
                        </svg>
                    </div>
                    <h4>Nenhuma feira registrada</h4>
                    <p>Crie sua primeira feira para começar a controlar seus gastos</p>
                    <button className="btn-nova-feira btn-empty" onClick={() => setShowModal(true)}>
                        <IoAdd /> Nova feira
                    </button>
                </div>
            ) : (
                <div className="feira-list">
                    {(() => {
                        const ativas = feiras.filter(
                            (f) => f.status === "em_andamento" || f.status === "andamento" || f.status === "pausada"
                        );
                        const finalizadas = feiras.filter(
                            (f) => f.status === "finalizada" || f.status === "cancelada"
                        );

                        const renderSection = (titulo, lista) => {
                            if (lista.length === 0) return null;
                            return (
                                <div className="feira-section">
                                    <h4 className="feira-section-title">{titulo}</h4>
                                    <div className="feira-section-list">
                                        {lista.map((feira) => (
                                            <FeiraCardItem
                                                key={feira.id}
                                                feira={feira}
                                                onClick={(id) => navigate(`/feira/${id}`)}
                                                onDelete={handleDelete}
                                            />
                                        ))}
                                    </div>
                                </div>
                            );
                        };

                        return (
                            <>
                                {renderSection("Feiras ativas", ativas)}
                                {renderSection("Feiras finalizadas", finalizadas)}
                            </>
                        );
                    })()}
                </div>
            )}

            {showModal && (
                <div className="modal-overlay" onClick={handleCancel}>
                    <div className="modal-box" onClick={(e) => e.stopPropagation()}>
                        <h3>Nova feira</h3>
                        <div className="modal-field">
                            <label>Nome da feira</label>
                            <input
                                type="text"
                                placeholder="Ex: Feira Semanal"
                                value={nome}
                                onChange={(e) => setNome(e.target.value)}
                                autoFocus
                            />
                        </div>
                        <div className="modal-field">
                            <label>Orçamento (R$)</label>
                            <input
                                type="number"
                                placeholder="Ex: 500"
                                value={orcamento}
                                onChange={(e) => setOrcamento(e.target.value)}
                                min="0"
                                step="0.01"
                            />
                        </div>
                        <div className="modal-actions">
                            <button className="btn-cancelar" onClick={handleCancel} disabled={saving}>
                                Cancelar
                            </button>
                            <button
                                className="btn-criar"
                                onClick={handleCreate}
                                disabled={saving || !nome.trim() || !orcamento}
                            >
                                {saving ? "Criando..." : "Criar feira"}
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default Feira;

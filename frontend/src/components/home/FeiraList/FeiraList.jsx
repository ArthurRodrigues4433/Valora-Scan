import { useState, useEffect } from "react";
import "./FeiraList.css";
import FeiraCard from "../FeiraCard/FeiraCard";
import api from "../../../services/api";

const FeiraList = () => {
    const [feiras, setFeiras] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchFeiras = async () => {
            try {
                const response = await api.get("/feiras/feira/resumo");
                setFeiras(response.data);
            } catch (error) {
                console.error("Erro ao buscar feiras:", error);
            } finally {
                setLoading(false);
            }
        };
        fetchFeiras();
    }, []);

    if (loading) {
        return (
            <section className="container-feiras">
                <SectionTitle title="Feiras recentes" />
                <div className="loading-state">
                    <div className="spinner"></div>
                </div>
            </section>
        );
    }

    if (feiras.length === 0) {
        return (
            <section className="container-feiras">
                <SectionTitle title="Feiras recentes" />
                <EmptyState />
            </section>
        );
    }

    return (
        <section className="container-feiras">
            <SectionTitle title="Feiras recentes" />
            {feiras.map((feira) => (
                <FeiraCard
                    key={feira.id}
                    id={feira.id}
                    nome={feira.nome}
                    data={feira.data}
                    economia={feira.economia.toFixed(2).replace('.', ',')}
                    gastoAtual={`R$ ${feira.gasto_atual.toFixed(2).replace('.', ',')}`}
                    gastoTotal={`R$ ${feira.gasto_total.toFixed(2).replace('.', ',')}`}
                    progresso={feira.progresso}
                />
            ))}
        </section>
    );
};

const EmptyState = () => (
    <div className="empty-state">
        <div className="empty-icon">
            <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                <path d="M3 3h18v18H3zM3 9h18M9 21V9" />
            </svg>
        </div>
        <h4>Nenhuma feira registrada</h4>
        <p>Crie sua primeira feira para começar a controlar seus gastos</p>
        <button className="btn-primary">+ Nova Feira</button>
    </div>
);

const SectionTitle = ({ title }) => (
    <div className="section-title">
        <h3>{title}</h3>
        <button>Ver tudo</button>
    </div>
);

export default FeiraList;
import { useState, useEffect, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import "./FeiraList.css";
import FeiraCard from "../FeiraCard/FeiraCard";
import api from "../../../services/api";

const FeiraList = () => {
    const [feiras, setFeiras] = useState([]);
    const [loading, setLoading] = useState(true);
    const [mostrarMais, setMostrarMais] = useState(false);
    const [erro, setErro] = useState(null);
    const MAX_FEIRAS = 5;

    useEffect(() => {
        const buscar = async () => {
            try {
                setErro(null);
                const { data } = await api.get("/feiras/feira/resumo");
                setFeiras(Array.isArray(data) ? data : []);
            } catch (e) {
                console.error("Erro ao buscar feiras:", e);
                setErro(e);
                setFeiras([]);
            } finally {
                setLoading(false);
            }
        };
        buscar();
    }, []);

    const ordenadas = useMemo(() => {
        const peso = {
            em_andamento: 0,
            andamento: 0,
            pausada: 1,
            finalizada: 2,
            cancelada: 3,
        };

        return [...feiras].sort((a, b) => {
            const pa = peso[a?.status] ?? 9;
            const pb = peso[b?.status] ?? 9;

            if (pa !== pb) return pa - pb;

            const da = a?.created_at ? new Date(a.created_at).getTime() : 0;
            const db = b?.created_at ? new Date(b.created_at).getTime() : 0;

            return db - da;
        });
    }, [feiras]);

    const exibidas = mostrarMais ? ordenadas : ordenadas.slice(0, MAX_FEIRAS);
    const temMais = ordenadas.length > MAX_FEIRAS;

    const tentarNovamente = () => {
        setLoading(true);
        setErro(null);
        api.get("/feiras/feira/resumo")
            .then(res => setFeiras(Array.isArray(res.data) ? res.data : []))
            .catch(e => {
                console.error("Erro ao buscar feiras:", e);
                setErro(e);
            })
            .finally(() => setLoading(false));
    };

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

    if (erro) {
        return (
            <section className="container-feiras">
                <SectionTitle title="Feiras recentes" />
                <div className="error-state">
                    <p>Não foi possível carregar as feiras</p>
                    <button className="btn-primary" onClick={tentarNovamente}>Tentar novamente</button>
                </div>
            </section>
        );
    }

    if (ordenadas.length === 0) {
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
            {exibidas.map((f) => (
                <FeiraCard
                    key={f.id}
                    id={f.id}
                    nome={f.nome}
                    data={f.dataFormatada || f.data}
                    status={f.status}
                    economia={Number(f.economia).toFixed(2).replace(".", ",")}
                    gastoAtual={`R$ ${Number(f.gasto_atual).toFixed(2).replace(".", ",")}`}
                    gastoTotal={`R$ ${Number(f.gasto_total).toFixed(2).replace(".", ",")}`}
                    progresso={f.progresso}
                />
            ))}
            {temMais && (
                <button className="btn-ver-mais" onClick={() => setMostrarMais(true)}>
                    Ver mais ({ordenadas.length - MAX_FEIRAS})
                </button>
            )}
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
    </div>
);

const SectionTitle = ({ title }) => {
    const navigate = useNavigate();
    return (
        <div className="section-title">
            <h3>{title}</h3>
            <button onClick={() => navigate("/feiras")}>Ver tudo</button>
        </div>
    );
};

export default FeiraList;

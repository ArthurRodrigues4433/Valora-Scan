import { useState, useEffect } from 'react';
import api from "../../../services/api";
import "./Stats.css";

const Stats = () => {
    const [stats, setStats] = useState(null);
    const [error, setError] = useState(null);

    useEffect(() => {
        api.get("/relatorios/economia")
            .then((res) => setStats(res.data))
            .catch((err) => {
                console.error("Erro ao carregar estatísticas:", err);
                setError(err);
            });
    }, []);

    const gastoReal = stats ? Number(stats.gasto_real || 0) : 0;
    const economia = stats ? Number(stats.economia || 0) : 0;
    const itensEscaneados = stats ? Number(stats.itens_escaneados || 0) : 0;

    return (
        <section className="container-estatisticas">
            <StatsCard
                label="Gasto total"
                value={`R$ ${gastoReal.toFixed(2).replace(".", ",")}`}
                subtext={`Economia: R$ ${economia.toFixed(2).replace(".", ",")}`}
                highlighted={false}
            />
            <StatsCard
                label="Itens escaneados"
                value={String(itensEscaneados)}
                subtext="Este mês"
                highlighted={true}
            />
        </section>
    );
};

const StatsCard = ({ label, value, subtext, highlighted }) => (
    <div className={`card-estatistica ${highlighted ? 'destaque' : ''}`}>
        <p>{label}</p>
        <h2>{value}</h2>
        <small>{subtext}</small>
    </div>
);

export default Stats;
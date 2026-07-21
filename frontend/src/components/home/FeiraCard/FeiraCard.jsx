import { useNavigate } from "react-router-dom";
import "./FeiraCard.css";

const STATUS_CONFIG = {
    em_andamento: { label: "Em andamento", color: "#e6a817", bg: "rgba(230, 168, 23, 0.1)" },
    finalizada: { label: "Finalizada", color: "#e74c3c", bg: "rgba(231, 76, 60, 0.1)" },
    cancelada: { label: "Cancelada", color: "#e74c3c", bg: "rgba(231, 76, 60, 0.1)" },
    pausada: { label: "Pausada", color: "#e6a817", bg: "rgba(230, 168, 23, 0.1)" },
};

const FeiraCard = ({ id, nome, data, status, economia, gastoAtual, gastoTotal, progresso }) => {
    const navigate = useNavigate();
    const cfg = STATUS_CONFIG[status] || STATUS_CONFIG.em_andamento;

    const handleClick = () => {
        navigate(`/feira/${id}`);
    };

    return (
        <div className="card-feira" onClick={handleClick}>
            <div className="linha-topo">
                <div>
                    <h4>{nome}</h4>
                    <small>{data}</small>
                </div>

                <span className="status-badge" style={{
                    color: cfg.color,
                    backgroundColor: cfg.bg,
                    border: `1px solid ${cfg.color}33`,
                }}>
                    {cfg.label}
                </span>
            </div>

            <div className="linha-valores">
                <span>Gasto</span>
                <span>{gastoAtual} / {gastoTotal}</span>
            </div>

            <div className="linha-economia">
                <span>Economia</span>
                <strong>R$ {economia}</strong>
            </div>

            <ProgressBar progresso={progresso} />
        </div>
    );
};

const ProgressBar = ({ progresso }) => (
    <div className="barra">
        <div 
            className="progresso" 
            style={{ width: `${progresso}%` }}
        ></div>
    </div>
);

export default FeiraCard;
export { ProgressBar };
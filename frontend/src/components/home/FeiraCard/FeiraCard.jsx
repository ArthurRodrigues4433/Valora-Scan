import { useNavigate } from "react-router-dom";
import "./FeiraCard.css";

const FeiraCard = ({ id, nome, data, economia, gastoAtual, gastoTotal, progresso }) => {
    const navigate = useNavigate();

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

                <div className="economia">
                    <span>Economia</span>
                    <strong>R$ {economia}</strong>
                </div>
            </div>

            <div className="linha-valores">
                <span>Gasto</span>
                <span>{gastoAtual} / {gastoTotal}</span>
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
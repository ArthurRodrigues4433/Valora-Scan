import "./FeiraCard.css";

const FeiraCard = ({ nome, data, economia, gastoAtual, gastoTotal, progresso }) => {
    return (
        <div className="card-feira">
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
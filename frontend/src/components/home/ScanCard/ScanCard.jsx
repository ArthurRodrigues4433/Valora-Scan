import "./ScanCard.css";

const ScanCard = ({ nome, preco, economia, tempo }) => {
    return (
        <div className="card-scan">
            <div className="produto">
                <div className="icone-produto"></div>
                <div>
                    <h4>{nome}</h4>
                    <small>{tempo}</small>
                </div>
            </div>

            <div className="preco">
                <strong>{preco}</strong>
                <span>{economia}</span>
            </div>
        </div>
    );
};

export default ScanCard;
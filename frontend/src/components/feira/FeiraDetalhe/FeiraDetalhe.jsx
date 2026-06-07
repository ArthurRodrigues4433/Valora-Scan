import { useParams, useNavigate } from "react-router-dom";
import "./FeiraDetalhe.css";
import { IoScan, IoArrowBack } from "react-icons/io5";

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
    
    const handleBack = () => {
        navigate(-1);
    };
    
    const handleScanProduct = () => {
        navigate(`/scan/${id}`);
    };
    
    const feira = {
        id: id,
        nome: "Feira Semanal",
        data: "07/06/2026",
        gasto_total: 120.00,
        status: "em_andamento",
        itensScaneados: 12,
        itens: [
            { id: 1, nome: "Arroz 5kg", preco: 25.90, economia: 4.50, tempo: "10:30", tipo: "atacado", quantidade: 2 },
            { id: 2, nome: "Feijão 2kg", preco: 12.50, economia: 0, tempo: "10:35", tipo: "varejo", quantidade: 1 },
            { id: 3, nome: "Óleo de soja", preco: 8.90, economia: 1.20, tempo: "10:42", tipo: "atacado", quantidade: 3 },
            { id: 4, nome: "Açúcar 2kg", preco: 6.50, economia: 0, tempo: "10:48", tipo: "varejo", quantidade: 1 },
            { id: 5, nome: "Café 500g", preco: 15.70, economia: 2.30, tempo: "10:55", tipo: "atacado", quantidade: 2 },
        ]
    };
    
    const gastoParcial = feira.itens.reduce((total, item) => total + item.preco, 0);
    const economiaParcial = feira.itens.reduce((total, item) => total + (item.economia || 0), 0);
    
    const getStatusConfig = (status) =>
        STATUS_CONFIG[status] || STATUS_CONFIG.finalizada;

    return (
        <div className="feira-detalhe-container">
            <div className="feira-detalhe-header">
                <button className="btn-back" onClick={handleBack}>
                    <IoArrowBack />
                </button>
                <h2 className="feira-detalhe-title">{feira.nome}</h2>
                <span
                    className="feira-status"
                    style={{ color: getStatusConfig(feira.status).color, backgroundColor: getStatusConfig(feira.status).bg }}
                >
                    {getStatusConfig(feira.status).label}
                </span>
            </div>

            <div className="feira-detalhe-info">
                <div className="info-row">
                    <span className="info-label">Data</span>
                    <span className="info-value">{feira.data}</span>
                </div>
                <div className="info-row">
                    <span className="info-label">Itens scaneados</span>
                    <span className="info-value">{feira.itensScaneados}</span>
                </div>
                <div className="info-row">
                    <span className="info-label">Valor total da feira</span>
                    <span className="info-value">R$ {feira.gasto_total.toFixed(2).replace('.', ',')}</span>
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
                <div className="itens-list">
                    {feira.itens.map((item) => (
                        <ItemCard
                            key={item.id}
                            nome={item.nome}
                            preco={item.preco}
                            tempo={item.tempo}
                            tipo={item.tipo}
                            quantidade={item.quantidade}
                        />
                    ))}
                </div>
            </div>
        </div>
    );
};

const ItemCard = ({ nome, preco, tempo, tipo, quantidade }) => {
    const tipoConfig = {
        atacado: { label: "Atacado", bg: "#2f8d3f", color: "#fff" },
        varejo: { label: "Varejo", bg: "#3498db", color: "#fff" },
    };
    const config = tipoConfig[tipo] || tipoConfig.varejo;
    
    return (
        <div className="card-item">
            <div className="item-info">
                <div className="icone-item"></div>
                <div>
                    <h4>{nome}</h4>
                    <small>{tempo}</small>
                    <div className="item-tipo">
                        <span style={{ backgroundColor: config.bg, color: config.color }}>
                            {config.label}
                        </span>
                        <span className="item-quantidade">Quant: {quantidade}</span>
                    </div>
                </div>
            </div>
            <div className="item-preco">
                <strong>R$ {preco.toFixed(2).replace('.', ',')}</strong>
            </div>
        </div>
    );
};

export default FeiraDetalhe;
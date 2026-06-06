import { useState, useEffect } from "react";
import "./ScanList.css";
import ScanCard from "../ScanCard/ScanCard";
import api from "../../../services/api";

const ScanList = () => {
    const [scans, setScans] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchScans = async () => {
            try {
                const response = await api.get("/notas/scans");
                setScans(response.data);
            } catch (error) {
                console.error("Erro ao buscar scans:", error);
            } finally {
                setLoading(false);
            }
        };
        fetchScans();
    }, []);

    if (loading) {
        return (
            <section className="container-scans">
                <SectionTitle title="Últimos scans" />
                <div className="loading-state">
                    <div className="spinner"></div>
                </div>
            </section>
        );
    }

    if (scans.length === 0) {
        return (
            <section className="container-scans">
                <SectionTitle title="Últimos scans" />
                <EmptyStateScans />
            </section>
        );
    }

    return (
        <section className="container-scans">
            <SectionTitle title="Últimos scans" />
            {scans.map((scan) => (
                <ScanCard
                    key={scan.id}
                    nome={scan.nome}
                    preco={`R$ ${scan.preco.toFixed(2).replace('.', ',')}`}
                    economia={scan.economia !== 0 ? `R$ ${scan.economia.toFixed(2).replace('.', ',')}` : "-"}
                    tempo={scan.tempo}
                />
            ))}
        </section>
    );
};

const EmptyStateScans = () => (
    <div className="empty-state">
        <div className="empty-icon">
            <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                <path d="M12 18.5V12M12 8.5V5M4 8.5h16M4 15.5h16M4 21.5h16M4 3.5h16" />
            </svg>
        </div>
        <h4>Nenhum scan registrado</h4>
        <p>Escaneie um produto para registrar sua compra</p>
    </div>
);

const SectionTitle = ({ title }) => (
    <div className="section-title">
        <h3>{title}</h3>
        <button>Ver tudo</button>
    </div>
);

export default ScanList;
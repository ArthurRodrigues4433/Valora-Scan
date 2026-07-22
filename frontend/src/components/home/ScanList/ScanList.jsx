import { useState, useEffect, useMemo } from "react";
import "./ScanList.css";
import ScanCard from "../ScanCard/ScanCard";
import api from "../../../services/api";
import Loading from "../../common/Loading";
import ErrorMessage from "../../common/ErrorMessage";

const ScanList = () => {
    const [scans, setScans] = useState([]);
    const [loading, setLoading] = useState(true);
    const [erro, setErro] = useState(null);

    useEffect(() => {
        const fetchScans = async () => {
            try {
                setErro(null);
                const { data } = await api.get("/notas/scans");
                setScans(Array.isArray(data) ? data : []);
            } catch (error) {
                setErro(error);
                setScans([]);
            } finally {
                setLoading(false);
            }
        };
        fetchScans();
    }, []);

    const ordenados = useMemo(() => {
        return [...scans].sort((a, b) => {
            const da = a?.data ? new Date(a.data).getTime() : 0;
            const db = b?.data ? new Date(b.data).getTime() : 0;

            if (da !== db) return db - da;

            return (b?.id || 0) - (a?.id || 0);
        });
    }, [scans]);

    const tentarNovamente = () => {
        setLoading(true);
        setErro(null);
        api.get("/notas/scans")
            .then(res => setScans(Array.isArray(res.data) ? res.data : []))
            .catch(error => {
                setErro(error);
            })
            .finally(() => setLoading(false));
    };

    if (loading) {
        return (
            <section className="container-scans">
                <SectionTitle title="Últimos scans" />
                <Loading text="Carregando..." />
            </section>
        );
    }

    if (erro) {
        return (
            <section className="container-scans">
                <SectionTitle title="Últimos scans" />
                <ErrorMessage message="Não foi possível carregar os scans" onRetry={tentarNovamente} />
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
            <div className="lista-scans">
                {ordenados.map((scan) => (
                    <ScanCard
                        key={scan.id}
                        nome={scan.nome}
                        preco={`R$ ${Number(scan.preco).toFixed(2).replace(".", ",")}`}
                        economia={scan.economia !== 0 ? `R$ ${Number(scan.economia).toFixed(2).replace(".", ",")}` : "-"}
                        tempo={scan.tempo}
                    />
                ))}
            </div>
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
        <button></button>
    </div>
);

export default ScanList;

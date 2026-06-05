import "./ScanList.css";
import ScanCard from "../ScanCard/ScanCard";

const scansData = [
    { 
        id: 1, 
        nome: "Arroz Tio João 5kg", 
        preco: "R$ 28,50", 
        economia: "-R$ 4,40", 
        tempo: "2 min atrás" 
    },
    { 
        id: 2, 
        nome: "Leite Integral 1L", 
        preco: "R$ 4,79", 
        economia: "-R$ 0,50", 
        tempo: "1h atrás" 
    },
];

const ScanList = () => {
    return (
        <section className="container-scans">
            <SectionTitle title="Últimos scans" />
            
            {scansData.map((scan) => (
                <ScanCard
                    key={scan.id}
                    nome={scan.nome}
                    preco={scan.preco}
                    economia={scan.economia}
                    tempo={scan.tempo}
                />
            ))}
        </section>
    );
};

const SectionTitle = ({ title }) => (
    <div className="section-title">
        <h3>{title}</h3>
        <button>Ver tudo</button>
    </div>
);

export default ScanList;
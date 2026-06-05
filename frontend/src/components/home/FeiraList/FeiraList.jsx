import "./FeiraList.css";
import FeiraCard from "../FeiraCard/FeiraCard";

const feirasData = [
    { 
        id: 1, 
        nome: "Feira do mês", 
        data: "Hoje, 14:32", 
        economia: "78,20", 
        gastoAtual: "R$ 612,40", 
        gastoTotal: "R$ 800,00", 
        progresso: 72 
    },
    { 
        id: 2, 
        nome: "Churrasco fim de semana", 
        data: "Sáb, 10:12", 
        economia: "24,50", 
        gastoAtual: "R$ 287,00", 
        gastoTotal: "R$ 350,00", 
        progresso: 80 
    },
];

const FeiraList = () => {
    return (
        <section className="container-feiras">
            <SectionTitle title="Feiras recentes" />
            
            {feirasData.map((feira) => (
                <FeiraCard
                    key={feira.id}
                    nome={feira.nome}
                    data={feira.data}
                    economia={feira.economia}
                    gastoAtual={feira.gastoAtual}
                    gastoTotal={feira.gastoTotal}
                    progresso={feira.progresso}
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

export default FeiraList;
import "./QuickActions.css";
import { Link } from "react-router-dom";
import { RiQrScan2Line } from "react-icons/ri";
import { TbReplace } from "react-icons/tb";
import { BsCart4 } from "react-icons/bs";
import { IoTimeOutline } from "react-icons/io5";

const quickActionsData = [
    { id: 1, icon: <RiQrScan2Line />, label: "Novo Scan", to: "/scan" },
    { id: 2, icon: <BsCart4 />, label: "Nova Feira", to: "/novafeira" },
    { id: 3, icon: <TbReplace />, label: "Comparar", to: "/comparar" },
    { id: 4, icon: <IoTimeOutline />, label: "Histórico", to: "/historico" },
];

const QuickActions = () => {
    return (
        <section className="container-acesso-rapido">
            {quickActionsData.map((action) => (
                <Link key={action.id} to={action.to} className="card-acesso-rapido">
                    <QuickActionCard icon={action.icon} label={action.label} />
                </Link>
            ))}
        </section>
    );
};

const QuickActionCard = ({ icon, label }) => (
    <div className="card-acesso-rapido-content">
        {icon && <div className="icon">{icon}</div>}
        {!icon && <div className="icon"></div>}
        <span>{label}</span>
    </div>
);

export default QuickActions;
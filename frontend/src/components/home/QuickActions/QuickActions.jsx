import "./QuickActions.css";
import { Link } from "react-router-dom";
import { RiQrScan2Line } from "react-icons/ri";
import { MdStorefront } from "react-icons/md";
import { AiOutlineScan } from "react-icons/ai";
import { BsClockHistory } from "react-icons/bs";

const quickActionsData = [
    { id: 1, icon: <RiQrScan2Line />, label: "Novo Scan", to: "/scan" },
    { id: 2, icon: <MdStorefront />, label: "Nova Feira", to: "/feira/nova" },
    { id: 3, icon: <AiOutlineScan />, label: "Comparar", to: "/comparar" },
    { id: 4, icon: <BsClockHistory />, label: "Histórico", to: "/historico" },
];

const QuickActions = () => {
    return (
        <section className="container-acesso-rapido">
            {quickActionsData.map((action) => (
                <Link key={action.id} to={action.to} className="card-acesso-rapido">
                    <div className="icon">{action.icon}</div>
                    <span>{action.label}</span>
                </Link>
            ))}
        </section>
    );
};

export default QuickActions;

import "./BottomNav.css";
import { useNavigate } from "react-router-dom";
import { IoHomeOutline } from "react-icons/io5";
import { BsCart4 } from "react-icons/bs";
import { IoTimeOutline } from "react-icons/io5";
import { RxAvatar } from "react-icons/rx";

const bottomNavData = [
    { id: 1, icon: <IoHomeOutline />, label: "Home", to: "/home" },
    { id: 2, icon: <BsCart4 />, label: "Compras", to: "/feiras" },
    { id: 3, icon: <IoTimeOutline />, label: "Economia", to: "/economia" },
    { id: 4, icon: <RxAvatar />, label: "Perfil", to: "/perfil" },
];

const BottomNav = ({ activeId = 1 }) => {
    const navigate = useNavigate();
    
    return (
        <section className="bottom-nav">
            {bottomNavData.map((action) => (
                <div
                    key={action.id}
                    className={"card-nav" + (activeId === action.id ? " active" : "")}
                    onClick={() => navigate(action.to)}
                >
                    <QuickBottomNav icon={action.icon} label={action.label} />
                </div>
            ))}
        </section>
    );
};

const QuickBottomNav = ({ icon, label }) => (
    <div className="card-nav-content">
        <div className="icon">{icon}</div>
        <span>{label}</span>
    </div>
);

export default BottomNav;
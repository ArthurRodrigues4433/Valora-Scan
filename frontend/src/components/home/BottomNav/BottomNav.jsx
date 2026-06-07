import "./BottomNav.css";
import { NavLink } from "react-router-dom";
import { IoHomeOutline } from "react-icons/io5";
import { BsCart4 } from "react-icons/bs";
import { IoTimeOutline } from "react-icons/io5";
import { RxAvatar } from "react-icons/rx";

const bottomNavData = [
    { id: 1, icon: <IoHomeOutline />, label: "Home", to: "/home" },
    { id: 2, icon: <BsCart4 />, label: "Feira", to: "/feiras" },
    { id: 3, icon: <IoTimeOutline />, label: "Histórico", to: "/historico" },
    { id: 4, icon: <RxAvatar />, label: "Perfil", to: "/perfil" },
];

const BottomNav = () => {
    return (
        <section className="bottom-nav">
            {bottomNavData.map((action) => (
                <NavLink
                    key={action.id}
                    to={action.to}
                    className={({ isActive }) => "card-nav" + (isActive ? " active" : "")}
                    end
                >
                    <QuickBottomNav icon={action.icon} label={action.label} />
                </NavLink>
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
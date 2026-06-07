import { useState } from "react";
import "./Home.css";
import Header from "./Header/Header";
import QuickActions from "./QuickActions/QuickActions";
import Stats from "./Stats/Stats";
import FeiraList from "./FeiraList/FeiraList";
import ScanList from "./ScanList/ScanList";
import FloatingButton from "./FloatingButton/FloatingButton";
import BottomNav from "./BottomNav/BottomNav";
import Feira from "../feira/Feira";

const Home = () => {
    const [activeId, setActiveId] = useState(1);

    const renderContent = () => {
        switch (activeId) {
            case 2:
                return <Feira />;
            case 3:
                return <ScanList />;
            case 4:
                return (
                    <div className="perfil-generico">
                        <h2>Perfil</h2>
                        <p>Configurações do usuário</p>
                    </div>
                );
            case 1:
            default:
                return (
                    <>
                        <Header />
                        <QuickActions />
                        <Stats />
                        <FeiraList />
                        <ScanList />
                    </>
                );
        }
    };

    return (
        <div className="container-geral">
            <div className="main-content">
                {renderContent()}
            </div>
            <BottomNav activeId={activeId} onChange={setActiveId} />
        </div>
    );
};

export default Home;
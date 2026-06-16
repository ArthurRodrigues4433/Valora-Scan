import { useState } from "react";
import "./Home.css";
import Header from "./Header/Header";
import QuickActions from "./QuickActions/QuickActions";
import Stats from "./Stats/Stats";
import FeiraList from "./FeiraList/FeiraList";
import ScanList from "./ScanList/ScanList";
import FloatingButton from "./FloatingButton/FloatingButton";
import BottomNav from "./BottomNav/BottomNav";

const Home = () => {
    return (
        <div className="container-geral">
            <div className="main-content">
                <Header />
                <QuickActions />
                <Stats />
                <FeiraList />
                <ScanList />
            </div>
            <BottomNav activeId={1} />
        </div>
    );
};

export default Home;
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
            <Header />
            <QuickActions />
            <Stats />
            <FeiraList />
            <ScanList />
            <FloatingButton />
            <BottomNav />
        </div>
    );
};

export default Home;
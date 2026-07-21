import { Routes, Route } from "react-router-dom";
import Login from "../components/login/Login";
import Home from "../components/home/Home";
import Register from "../components/register/Register";
import Scan from "../components/scanner/Scan";
import Confirmacao from "../components/scanner/Confirmacao";
import Feira from "../components/feira/Feira";
import FeiraDetalhe from "../components/feira/FeiraDetalhe/FeiraDetalhe";
import Economia from "../components/economia/Economia";
import Perfil from "../components/perfil/Perfil";
import PrivateRoute from "../components/auth/PrivateRoute";

export default function AppRoutes() {
    return (
        <Routes>
            <Route path="/" element={<Login />} />
            <Route path="/auth/login" element={<Login />} />
            <Route path="/auth/register" element={<Register />} />
            <Route element={<PrivateRoute />}>
                <Route path="/home" element={<Home />} />
                <Route path="/feiras" element={<Feira />} />
                <Route path="/feira/:id" element={<FeiraDetalhe />} />
                <Route path="/feira/:id/scan" element={<Scan />} />
                <Route path="/feira/:id/confirmar" element={<Confirmacao />} />
                <Route path="/economia" element={<Economia />} />
                <Route path="/perfil" element={<Perfil />} />
            </Route>
        </Routes>
    )
}

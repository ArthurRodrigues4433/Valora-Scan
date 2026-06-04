import { Routes, Route } from "react-router-dom";
import Login from "../components/login/Login";
import Home from "../components/home/Home";
import Register from "../components/register/Register";

export default function AppRoutes() {
    return (
        <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/home" element={<Home />} />
            <Route path="/register" element={<Register />} />
        </Routes>
    )
}
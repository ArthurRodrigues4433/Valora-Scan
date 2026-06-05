import { Routes, Route } from "react-router-dom";
import Login from "../components/login/Login";
import Home from "../components/home/Home";
import Register from "../components/register/Register";
import PrivateRoute from "../components/auth/PrivateRoute";

export default function AppRoutes() {
    return (
        <Routes>
            <Route path="/auth/login" element={<Login />} />
            <Route path="/auth/register" element={<Register />} />


            <Route element={<PrivateRoute />}>
                <Route path="/home" element={<Home />} />
            </Route>
        </Routes>
    )
}
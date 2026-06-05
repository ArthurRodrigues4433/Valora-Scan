import { Navigate, Outlet } from "react-router-dom";

const PrivateRoute = () => {
    const token = localStorage.getItem('access_token');

    if (!token) {
        return <Navigate to="/auth/login" replace />;
    }

    return <Outlet />;  // ✅ Renderiza a rota filha (/home)
};

export default PrivateRoute;
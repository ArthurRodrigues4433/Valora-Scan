import "./Header.css"
import { useState, useEffect } from "react";
import api from "../../../services/api";
import { IoMdNotificationsOutline } from "react-icons/io";
import { WiStars } from "react-icons/wi";

const Header = () => {
    const [nomeUsuario, setNomeUsuario] = useState("");
    const [economia, setEconomia] = useState(null);
    const [carregando, setCarregando] = useState(true);

    useEffect(() => {
        const carregarDados = async () => {
            try {
                // Busca usuario e economia em paralelo
                const [usuarioRes, economiaRes] = await Promise.all([
                    api.get("/usuarios/me"),
                    api.get("/relatorios/economia"),
                ]);

                setNomeUsuario(usuarioRes.data.nome);
                setEconomia(economiaRes.data);
            } catch (erro) {
                console.error("Erro:", erro);
            } finally {
                setCarregando(false);
            }
        };

        carregarDados();
    }, []);

    if (carregando) {
        return (
            <header className="container-sidebar">
                <div className="header-top">
                    <h2>Carregando...</h2>
                </div>
            </header>
        );
    }

    const valorEconomia = Number(economia?.economia).toFixed(2).replace(".", ",") || "0,00";
    const percentual = Number(economia?.percentual_economia) || 0;

    return (
        <header className="container-sidebar">
            <div className="header-top">
                <div>
                    <h2>Olá, {nomeUsuario}</h2>
                    <h1>Quanto vai economizar hoje?</h1>
                </div>
                <div className="icon-notificacao"><IoMdNotificationsOutline /></div>
            </div>

            <div className="container-economia">
                <div className="economia-conteudo">
                    <span>ECONOMIA DO MÊS</span>
                    <WiStars className="star-icon" />
                </div>
                <h2>R$ {valorEconomia}</h2>
                <p>↗ +{percentual}% comparado ao mês passado</p>
                <div className="icon-economia"></div>
            </div>
        </header>
    );
};

export default Header;
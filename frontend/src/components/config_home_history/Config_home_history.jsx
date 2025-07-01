import { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import './Config_home_history.css';

const ConfigHomeHistory = () => {
    const [mensajes, setMensajes] = useState([]);

    // fetchHistorial como función dentro de useCallback para que no cambie de referencia
    const fetchHistorial = useCallback(async () => {
        try {
            const response = await axios.post('/api/get-user-history/', {}, { withCredentials: true });
            setMensajes(response.data);  // Directamente asignamos los mensajes que vienen del backend
        } catch (error) {
            // console.error("Error al obtener el historial de mensajes:", error);
            console.log("")
        }
    }, []);  // No depende de nada, siempre es la misma función

    useEffect(() => {
        fetchHistorial();  // Ejecuta la primera vez al cargar

        const interval = setInterval(() => {
            fetchHistorial();  // Ejecuta cada 5 minutos (300,000 ms)
        }, 300000);  // 5 minutos

        return () => clearInterval(interval);  // Limpia el intervalo al desmontar el componente
    }, [fetchHistorial]);

    return (
        <div className="history-home-square">
            <h1>Historial de mensajes</h1>
            <div className="history-cont">
                {mensajes.length > 0 ? (
                    mensajes.map((mensaje, index) => (
                        <div className="history-card" key={index}>
                            <h3 className="history-subject">
                                {mensaje.subject || "Sin asunto"} | {mensaje.sender || "Remitente desconocido"}
                            </h3>
                            <p className="history-summary">{mensaje.summary || "Sin resumen"}</p>
                        </div>
                    ))
                ) : (
                    <p className="no-messages">No hay mensajes en el historial.</p>
                )}
            </div>
        </div>
    );
};

export default ConfigHomeHistory;

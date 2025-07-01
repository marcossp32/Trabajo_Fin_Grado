import './Config_home_start.css';
import axios from 'axios';
import PropTypes from 'prop-types';
import { useState, useEffect } from 'react';

const Config_home_start = ({ userEmail, onMissingData }) => {
  const [isFlowActive, setIsFlowActive] = useState(() => {
    const stored = localStorage.getItem("flow_active");
    return stored === "true";
  });

  useEffect(() => {
    localStorage.setItem("flow_active", isFlowActive);
  }, [isFlowActive]);

  const startFlow = async () => {
    if (!userEmail) {
      // console.error("No se encontró el email del usuario.");
      return;
    }

    try {
      const validationResponse = await axios.post(
        '/api/start-flow-request/',
        { email: userEmail },
        { withCredentials: true }
      );

      if (validationResponse.data.error) {
        const missingFields = validationResponse.data.missing_fields || [];
        // console.error("Faltan campos:", missingFields);
        onMissingData(missingFields);
        return;
      }

      // Si todo está bien, limpiamos errores anteriores
      onMissingData(null);

      const startResponse = await axios.post(
        '/api/start-flow/',
        { email: userEmail, action: 'start' },
        { withCredentials: true }
      );

      if (startResponse.status === 200) {
        // console.log("Flujo iniciado:", startResponse.data);
        setIsFlowActive(true);
      } // else {
      //   console.error("Error iniciando el flujo:", startResponse.status);
      // }
    } catch (error) {
      // console.error("Error al iniciar el flujo:", error);

      if (error.response && error.response.data) {
        // console.error("Respuesta del backend:", error.response.data);
        onMissingData(error.response.data.missing_fields || []);
      } //else {
      //   setLocalError("Error al iniciar el flujo. Inténtalo de nuevo.");
      // }
    }
  };

  const stopFlow = async () => {
    if (!userEmail) {
      // console.error("No se encontró el email del usuario.");
      return;
    }

    try {
      const stopResponse = await axios.post(
        '/api/start-flow/',
        { email: userEmail, action: 'stop' },
        { withCredentials: true }
      );

      if (stopResponse.status === 200) {
        // console.log("Flujo detenido:", stopResponse.data);
        setIsFlowActive(false);
      } //else {
      //   console.error("Error deteniendo el flujo:", stopResponse.status);
      // }
    } catch (error) {
      // console.error("Error al detener el flujo:", error);
    }
  };

  const toggleFlow = () => {
    if (isFlowActive) {
      stopFlow();
    } else {
      startFlow();
    }
  };

  return (
    <div className="start-home-square">
      <h1>{isFlowActive ? 'Flujo activo' : 'Iniciar flujo'}</h1>
      <p>
        Al pulsar el botón, se {isFlowActive ? 'detendrá' : 'activará'} la inteligencia artificial encargada de la gestión automatizada de tus correos electrónicos.
      </p>
      <button type="button" className="start-ai" onClick={toggleFlow}>
        {isFlowActive ? 'Parar' : 'Iniciar'}
      </button>
    </div>
  );
};

Config_home_start.propTypes = {
  userEmail: PropTypes.string.isRequired,
  onMissingData: PropTypes.func.isRequired,
};

export default Config_home_start;

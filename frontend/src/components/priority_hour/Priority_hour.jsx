import './Priority_hour.css';
import { useState } from 'react';
import Form_config_input from '@components/form_config_input/Form_config_input';

const Priority_hour = ({ onChange, onSave }) => {
  const [status, setStatus] = useState('idle'); // 'idle', 'loading', 'success', 'error'

  const handleClick = async () => {
    setStatus('loading');
    try {
      await onSave();  // no hay campos obligatorios, asumimos siempre válido
      setStatus('success');
    } catch (error) {
      // console.error("Error al guardar datos de prioridad:", error);
      setStatus('error');
    }

    setTimeout(() => setStatus('idle'), 4000);
  };

  const renderButtonContent = () => {
    if (status === 'loading') {
      return <span className="loader"></span>;
    } else if (status === 'success') {
      return <span className="status-icon">✔</span>;
    } else if (status === 'error') {
      return <span className="status-icon">✖</span>;
    } else {
      return 'Guardar';
    }
  };

  return (
    <div className="priority-hour-square">
      <h1>Horario preferente</h1>
      <p>Actualiza aquí tu horario prioritario</p>

      <div className="priority-hour-cont">
        <div className="row">
          <Form_config_input 
            label="Inicio horario prioritario" 
            placeholder="Inserta la hora de inicio de la jornada prioritaria" 
            name="init_priority_schedule" 
            type="time"
            onChange={onChange}
          />
          <Form_config_input 
            label="Fin horario prioritario" 
            placeholder="Inserta la hora de finalización de la jornada prioritaria" 
            name="end_priority_schedule" 
            type="time"
            onChange={onChange}
          />
        </div>

        <div className="row">
          <Form_config_input 
            label="Días prioritarios" 
            name="priority_days" 
            type="checkbox-group" 
            options={[
              { value: "monday", label: "Lunes" },
              { value: "tuesday", label: "Martes" },
              { value: "wednesday", label: "Miércoles" },
              { value: "thursday", label: "Jueves" },
              { value: "friday", label: "Viernes" },
              { value: "saturday", label: "Sábado" },
              { value: "sunday", label: "Domingo" },
            ]}
            onChange={onChange}
          />
        </div>
      </div>

      <button className={`save-button status-${status}`} onClick={handleClick}>
        {renderButtonContent()}
      </button>
    </div>
  );
};

export default Priority_hour;

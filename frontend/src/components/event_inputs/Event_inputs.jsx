import { useState } from 'react';
import './Event_inputs.css';
import Form_config_input from '@components/form_config_input/Form_config_input';

const Event_inputs = ({ eventData, onChange, onSave }) => {
    const [status, setStatus] = useState('idle'); // 'idle', 'loading', 'success', 'error'

    const handleClick = async () => {
      setStatus('loading');
      try {
        await onSave();  // no hay campos obligatorios, asumimos siempre válido
        setStatus('success');
      } catch (error) {
        console.error("Error al guardar datos de prioridad:", error);
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
    <div className="event-info-square">
      <h1>Eventos</h1>
      <p>Configura tus preferencias de reuniones</p>

      <div className="event-info-cont">
        <div className="row">
          <Form_config_input 
            label="Duración estándar de sus reuniones (minutos)" 
            placeholder="Indica la duración estándar de tus reuniones" 
            name="meeting_duration" 
            type="number"
            onChange={onChange}
          />
        </div>
        <div className="row">
          <Form_config_input 
            label="Límite de reuniones por día" 
            placeholder="Indica un límite de reuniones por día" 
            name="meeting_limit" 
            type="number"
            onChange={onChange}
          />
        </div>
        <div className="row">
          <Form_config_input 
            label="Días apagado" 
            name="days_off" 
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
        <div className="row">
          <Form_config_input 
            label="Desea recibir notificaciones cuando se programen nuevas reuniones" 
            name="notify_meeting" 
            type="checkbox"
            checked={Boolean(eventData.notify_meeting)}
            onChange={onChange}
          />
        </div>
        <div className="row">
          <Form_config_input 
            label="Desea permitir que el asistente proponga nuevas horas o días si rechaza una reunión" 
            name="meeting_porpose" 
            type="checkbox"
            checked={Boolean(eventData.meeting_porpose)}
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

export default Event_inputs;

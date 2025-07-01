import { useState } from 'react';
import './Schedule_days.css';
import Form_config_input from '@components/form_config_input/Form_config_input';

const Schedule_days = ({ onChange, onSave }) => {
  const [status, setStatus] = useState('idle'); // 'idle', 'loading', 'success', 'error'

  const handleClick = async () => {
    setStatus('loading');
    try {
      const result = await onSave(); // debe devolver true o false

      if (result === true) {
        setStatus('success');
      } else {
        setStatus('error');
      }
    } catch (err) {
      // console.error("Error en onSave:", err);
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
    <div className="schedule-days-square">
      <h1>Configura tu disponibilidad</h1>
      <p>Selecciona los días en los que no estarás disponible para reuniones y define el margen de tiempo entre ellas.</p>

      <div className="row">
        <Form_config_input 
          label="Días no disponibles para reuniones" 
          name="days_blocked" 
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
        <Form_config_input 
          label="Margen entre reuniones (minutos)" 
          placeholder="Inserta cuanto margen quieres entre reuniones" 
          name="margin_event" 
          type="number" 
          onChange={onChange}
        />
      </div>

      <button className={`save-button status-${status}`} onClick={handleClick}>
        {renderButtonContent()}
      </button>
    </div>
  );
};

export default Schedule_days;

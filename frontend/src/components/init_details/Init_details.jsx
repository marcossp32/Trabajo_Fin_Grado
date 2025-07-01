import './Init_details.css';
import { useState } from 'react';
import Form_config_input from '@components/form_config_input/Form_config_input';

const Init_details = ({ onChange, onSave, missingData }) => {
  const [status, setStatus] = useState('idle'); // 'idle', 'loading', 'success', 'error'

  const handleClick = async () => {
    setStatus('loading');
    try {
      const result = await onSave();
      if (result === true) {
        setStatus('success');
      } else {
        setStatus('error');
      }
    } catch (err) {
      setStatus('error');
      // console.log("Error", err);
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
    <div className="details-info-square">
      <h1>Detalles adicionales</h1>
      <p>Proporciona información extra o detalles que quieras resaltar</p>
      
      <div className="init-details-cont">
        <Form_config_input
          label="Detalles" 
          placeholder="Inserta detalles sobre tu persona o preferencias que quieras comentar" 
          name="details" 
          type="textarea"
          onChange={onChange}
          fullWidth 
        />

        <button className={`save-button status-${status}`} onClick={handleClick}>
          {renderButtonContent()}
        </button>
      </div> 
    </div>
  );
};

export default Init_details;

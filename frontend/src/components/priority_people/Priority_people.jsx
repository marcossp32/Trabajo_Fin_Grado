import './Priority_people.css';
import Form_config_input from '@components/form_config_input/Form_config_input';

const Priority_people = ({ onChange }) => {

    // Meter logica para el boton de guardar, llamada a la api

    return (
        <div className="priority-people-square">
            <h1>Personas y asuntos importantes</h1>
            <p>Actualiza aqui tus personas y asuntos prioritarios</p>

            <div className="row">
                <Form_config_input 
                    label="Asustos prioritarios" 
                    placeholder="Inserta tus asuntos prioritarios reparados por ," 
                    name="priority_subject" 
                    type="text" 
                    onChange={onChange}
                />
            </div>

            <div className="row">
                <Form_config_input 
                    label="Personas prioritarias" 
                    placeholder="Inserta tus personas prioritarias reparados por ," 
                    name="priority_people" 
                    type="text" 
                    onChange={onChange}
                />
            </div>
            
          
        </div>
    );
};

export default Priority_people;

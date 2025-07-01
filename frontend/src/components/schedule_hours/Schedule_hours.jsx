import './Schedule_hours.css'
import Form_config_input from '@components/form_config_input/Form_config_input'

const Schedule_hours = ({ onChange, missingData }) =>{
    return(
        <div className="schedue-hours-square">
            <h1>Horario</h1>
            <p>Actualiza aquí tus preferencias de horario</p>

            <div className="init-personal-cont">
                <div className="row">
                    <Form_config_input 
                        label="Inicio horario laboral" 
                        placeholder="Inserta la hora de inicio de jornada laboral" 
                        name="init_schedule" 
                        type="time" 
                        onChange={onChange}
                        error={missingData?.init_schedule}
                        required={true}
                    />
                    <Form_config_input 
                        label="Fin horario laboral" 
                        placeholder="Inserta la hora de finalización de jornada laboral" 
                        name="end_schedule" 
                        type="time" 
                        onChange={onChange}
                        error={missingData?.end_schedule}
                        required={true}
                    />
                </div>

                <div className="row">
                    <Form_config_input 
                        label="Inicio horario bloqueado" 
                        placeholder="Inserta la hora de inicio en la que no quieres reuniones" 
                        name="init_schedule_no_meeting" 
                        type="time" 
                        onChange={onChange}
                    />
                    <Form_config_input 
                        label="Fin horario bloqueado" 
                        placeholder="Inserta la hora de finalización en la que no quieres reuniones" 
                        name="end_schedule_no_meeting" 
                        type="time" 
                        onChange={onChange}
                    />
                </div>
            </div>
        </div>
    )
}

export default Schedule_hours;

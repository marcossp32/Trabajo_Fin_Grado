import './Init_personal_info.css';
import Form_config_input from '@components/form_config_input/Form_config_input';

const Init_personal_info = ({ onChange, missingData }) => {
    return (
        <div className="personal-info-square">
            <h1>Información personal</h1>
            <p>Actualiza aquí tu información personal</p>

            <div className="init-personal-cont">
                <div className="row">
                    <Form_config_input 
                        label="Nombre completo" 
                        placeholder="Inserta tu nombre completo" 
                        name="fullname" 
                        type="text"
                        onChange={onChange}
                        error={missingData?.fullname} // Se aplica error si falta el dato
                        required={true}
                    />
                    <Form_config_input 
                        label="Cargo" 
                        placeholder="Inserta tu posición laboral" 
                        name="position" 
                        type="text"
                        onChange={onChange}
                    />
                </div>

                <div className="row">
                    <Form_config_input 
                        label="Idioma" 
                        placeholder="Selecciona tu idioma" 
                        name="language" 
                        type="option" 
                        options={[
                            { value: "es", label: "Español" },
                            { value: "en", label: "Inglés" },
                            { value: "fr", label: "Francés" },
                            { value: "de", label: "Alemán" }
                        ]}
                        onChange={onChange}
                        fullWidth 
                        error={missingData?.language} // Se aplica error si falta el dato
                        required={true}
                    />
                </div>
            </div>
        </div>
    );
};

export default Init_personal_info;

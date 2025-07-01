import './Start_title_section.css';

const Start_title_section = ({ AuthState,onOpenConnect }) => {

    const handleStartClick = (e) => {
        e.preventDefault();
        if (AuthState) {
            window.location.href = "/configurator"; // Redirige si está autenticado
        } else {
            onOpenConnect(); // Muestra Connect si no está autenticado
        }
    };

    return (
        <div className="container-start">
            <h1 className="title-start">Simplifica tu correo, potencia tu día</h1>
            <p className="text-start">
                Nuestro asistente inteligente analiza tus correos, identifica las necesidades clave y toma acciones automáticas para
                gestionar tus reuniones y optimizar tu tiempo y tu agenda.
            </p>
            <button className="button-start" onClick={handleStartClick}>Comienza</button>
        </div>
    );
};

export default Start_title_section;

import axios from 'axios';
import './Connect.css';

const Connect = ({ show, onClose, alertMessage }) => {

    const handleGoBack = () => {
        if (onClose) onClose(); // Llama a la función para cerrar
    };

    const handleOauth = async () => {
        try {
            // Llamada al backend para obtener la URL de autorización
            const response = await axios.get('/api/connect', { withCredentials: true });
            if (response.status === 200 && response.data.authorization_url) {
                // Redirigir al usuario a la URL de autorización
                window.location.href = response.data.authorization_url;
            } else {
                alert('Hubo un problema al conectarse. Inténtalo de nuevo.');
            }
        } catch (error) {
            alert('Error al conectar. Verifica tu conexión o inténtalo más tarde.');
            // console.error(error);
        }
    };

    return (
        <div className={`container-main-blur ${show ? 'visible' : ''}`}>
            <div className="container-main">

                {/* <a href="https://es.pikbest.com//png-images/robot-3d-sobre-fondo-transparente_10408759.html">Gratis  elementos graficos de es.pikbest.com</a>*/}

                <div className="tobby-hello-connect">
                    <img src="/img/tobby-hello.png" alt="Tobby waving" />
                </div>
                <div className="go-back">
                    <a onClick={handleGoBack}>
                        <img src="/svg/arrow-left.svg" alt="Go back" />
                    </a>
                </div>
                <div className="container-title-1">
                    <h1>AISERV</h1>
                </div>
                <div className="container-title-2">
                    <h1>CONECTA TU CUENTA</h1>
                </div>
                {alertMessage && <div className="alert">{alertMessage}</div>}
                <div className="appBut-container">
                    <a onClick={handleOauth} className="google-btn">
                        <img src="https://developers.google.com/identity/images/g-logo.png" alt="Google logo" />
                        Continua con Google
                    </a>
                </div>
                <p>
                    Al conectar tu cuenta estarás aceptando nuestros{' '}
                    <a href="/info">términos de uso</a>
                </p>
            </div>
        </div>
    )
}

export default Connect

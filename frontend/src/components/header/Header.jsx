import { useState, useEffect } from 'react';
import axios from 'axios';
import Connect from '@components/connect/Connect';
import './Header.css';
import { useNavigate, useLocation } from 'react-router-dom';


const Header = ({ setAuthState }) => {
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [showConnect, setShowConnect] = useState(false);
    const [userData, setUserData] = useState({ username: '', is_active_auto: false });
    const [alertMessage, setAlertMessage] = useState('')
    const [darkMode, setDarkMode] = useState(() => {
        return localStorage.getItem('theme') ? localStorage.getItem('theme') === 'dark' : true;
    });

    const navigate = useNavigate();
    const location = useLocation();

    const scrollToId = (id) => {
        const el = document.getElementById(id);
        if (el) {
            el.scrollIntoView({ behavior: 'smooth' });
        }
    };

    const handleNavigation = (sectionId) => {
        if (location.pathname !== '/') {
            navigate('/', { state: { scrollTo: sectionId } });
        } else {
            scrollToId(sectionId);
        }
    };
    

    // Función para alternar el modo dark/light
    const toggleTheme = () => {
        const newTheme = darkMode ? 'light' : 'dark';
        setDarkMode(!darkMode);
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
    };

    // Establecer el tema basado en el almacenamiento local
    useEffect(() => {
        const savedTheme = localStorage.getItem('theme') || 'dark';  // Por defecto "dark"
        document.documentElement.setAttribute('data-theme', savedTheme);
        setDarkMode(savedTheme === 'dark');
    }, []);
    


    // Función para obtener los datos del usuario desde el backend
    const fetchUserData = async () => {
        try {
            const response = await axios.post('/api/user/data/', {}, { withCredentials: true });
            if (response.status === 200) {
                const { username, is_active_auto } = response.data;
                setUserData({ username, is_active_auto });
                setIsAuthenticated(true);
                setAuthState(true);
            } else {
                // console.error('Error al obtener los datos del usuario');
                console.log("")
            }
        } catch (error) {
            // console.error('Error al procesar los datos del usuario:', error);
            console.log("")
        }
    };

    useEffect(() => {
        fetchUserData();
    }, []);

    const handleLogout = async () => {
        try {
            const response = await axios.post('/api/logout/', {}, { withCredentials: true });
            if (response.status === 200) {
                setIsAuthenticated(false);
                setAuthState(false);
                setUserData({ username: '', is_active_auto: false });
            } else {
                // console.error('Error al cerrar sesión');
                console.log("")
            }
        } catch (error) {
            // console.error('Error al procesar el cierre de sesión:', error);
            console.log("")
        }
    };
        


    const handleConnect = () => {
        setShowConnect(true)
    }

    const [isOpen, setIsOpen] = useState(false);

    const toggleOverlay = () => {
        setIsOpen((prev) => !prev);
    };

    return (
        <>
            <header>
                <div className="header-left">
                    <h1>AISERV</h1>
                </div>

                {/* Contenedor del perfil en la parte de la cabecera */}
                <div className="header-right">

                    {/* Este es el a del icono del dark/light mode */}
                    <a onClick={toggleTheme}>
                        <img src={darkMode ? '/svg/moon.svg' : '/svg/sun.svg'} alt="Mode toggle" />
                    </a>
                    <a className="head-r-a" onClick={() => handleNavigation('about-scroll')}>About</a>
                    <a className="head-r-a" onClick={() => handleNavigation('product-title')}>Producto</a>
                    <a className="head-r-a" onClick={() => navigate('/info#contact')}>Contacto</a>


                    {isAuthenticated ? (
                        <div className="profile-container" >
                            <a id="a-profile" onClick={toggleOverlay}>

                                {/* Aqui se pude poner el icono de la persona si no tiene imagen en el correo pero si tiene imagen podria poner la imagen */}

                                <svg viewBox="-77 -19 629 629.33435" xmlns="http://www.w3.org/2000/svg">
                                    <path
                                        stroke="currentColor"
                                        strokeWidth="5"
                                        d="m233.371094 294.5c81.328125 0 147.25-65.925781 147.25-147.25 0-81.320312-65.921875-147.25-147.25-147.25-81.320313 0-147.25 65.929688-147.25 147.25.0625 81.296875 65.953125 147.1875 147.25 147.25zm0-269.542969c67.542968 0 122.292968 54.75 122.292968 122.292969s-54.75 122.292969-122.292968 122.292969c-67.535156 0-122.292969-54.75-122.292969-122.292969.113281-67.492188 54.800781-122.183594 122.292969-122.292969zm0 0"
                                    ></path>
                                    <path d="m233.371094 331.3125c-64.011719 0-123.539063 24.832031-167.710938 70.007812-44.800781 45.796876-69.386718 108.3125-69.386718 176.203126.019531 6.882812 5.597656 12.457031 12.480468 12.476562h449.238282c6.886718-.019531 12.457031-5.59375 12.476562-12.476562 0-67.761719-24.582031-130.40625-69.378906-176.078126-44.175782-45.175781-103.699219-70.132812-167.71875-70.132812zm-211.886719 233.730469c2.746094-56.402344 24.582031-107.941407 61.894531-146.128907 39.433594-40.308593 92.71875-62.515624 149.871094-62.515624s110.4375 22.207031 149.867188 62.515624c37.4375 38.1875 59.152343 89.726563 61.898437 146.128907zm0 0"></path>
                                </svg>
                            </a>
                            <div className={`profile-overlay ${isOpen ? "open" : ""}`}>
                                <span>Hola, {userData.username}</span>
                                <a onClick={handleLogout}>
                                    Cerrar Sesión
                                </a>
                            </div>
                        </div>
                    ) : (
                        <a id="a-connect" onClick={handleConnect}>
                            Conéctate
                        </a>
                    )}
                </div>
            </header>

            {/* Componente Connect */}
            <Connect show={showConnect} onClose={() => setShowConnect(false)} alertMessage={alertMessage}/>
        </>
    )
}

export default Header

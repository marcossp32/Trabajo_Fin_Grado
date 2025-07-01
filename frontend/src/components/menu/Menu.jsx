import './Menu.css';
import '@fortawesome/fontawesome-free/css/all.min.css';
import { useState } from 'react';

const Menu = ({ setSelectedSection, isMenuOpen, setIsMenuOpen, highlightSections = [] }) => {
    const [activeSection, setActiveSection] = useState('home');
    const disabledSections = ['metrics', 'perfil'];
    const [darkMode, setDarkMode] = useState(() => {
        return localStorage.getItem('theme') ? localStorage.getItem('theme') === 'dark' : true;
    });

    const handleMenuClick = (section, event) => {
        if (disabledSections.includes(section)) {
            event.preventDefault();
            event.stopPropagation();
            return;
        }
        setActiveSection(section);
        setSelectedSection(section);
    };

    // Función para alternar el modo dark/light
    const toggleTheme = () => {
        const newTheme = darkMode ? 'light' : 'dark';
        setDarkMode(!darkMode);
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
    };

    return (
        <section className={`menu ${isMenuOpen ? 'open' : ''}`}>
            <a href="/"><h1>AISERV</h1></a>
            <div className={`menu-toggle ${isMenuOpen ? 'open' : ''}`} onClick={() => setIsMenuOpen(!isMenuOpen)}>
                <div className="menu-circle"><i className={`fas ${isMenuOpen ? 'fa-chevron-left' : 'fa-chevron-right'}`}></i></div>
            </div>
            <ul className="config-elements">
                <p className="section-title">General</p>
                <li onClick={(e) => handleMenuClick('home', e)} className={activeSection === 'home' ? 'active' : ''}><i className="fas fa-home"></i> Home</li>
                <li onClick={(e) => handleMenuClick('metrics', e)} className={`${activeSection === 'metrics' ? 'active' : ''} ${disabledSections.includes('metrics') ? 'disabled' : ''}`}><i className="fas fa-chart-line"></i> Métricas</li>
                <li onClick={(e) => handleMenuClick('calendar', e)} className={`${activeSection === 'calendar' ? 'active' : ''} ${disabledSections.includes('calendar') ? 'disabled' : ''}`}><i className="fas fa-calendar-alt"></i> Calendario</li>
                <p className="section-title">Config</p>
                <li onClick={(e) => handleMenuClick('init', e)} className={`${activeSection === 'init' ? 'active' : ''} ${highlightSections.includes('init') ? 'highlight-error' : ''}`}><i className={`fas fa-rocket ${highlightSections.includes('init') ? 'icon-error' : ''}`}></i> Inicio</li>
                <li onClick={(e) => handleMenuClick('schedule', e)} className={`${activeSection === 'schedule' ? 'active' : ''} ${highlightSections.includes('schedule') ? 'highlight-error' : ''}`}><i className={`fas fa-clock ${highlightSections.includes('schedule') ? 'icon-error' : ''}`}></i> Horario</li>
                <li onClick={(e) => handleMenuClick('priority', e)} className={activeSection === 'priority' ? 'active' : ''}><i className="fas fa-layer-group"></i> Prioridad</li>
                <li onClick={(e) => handleMenuClick('event', e)} className={activeSection === 'event' ? 'active' : ''}><i className="fas fa-tasks"></i> Eventos</li>
                <p className="section-title">Otro</p>
                <li onClick={(e) => handleMenuClick('notify', e)} className={`${activeSection === 'notify' ? 'active' : ''} ${disabledSections.includes('notify') ? 'disabled' : ''}`}><i className="fas fa-bell"></i> Notificaciones</li>
                <li onClick={(e) => toggleTheme(e)} className={`${disabledSections.includes('mode') ? 'disabled' : ''}`}><i className="fas fa-adjust"></i> Mode</li>
            </ul>
            <div className={`profile-menu ${disabledSections.includes('perfil') ? 'disabled' : ''}`}></div>{/* <i className="fas fa-user-circle"></i> <p>Perfil</p> */}
        </section>
    );
};

export default Menu;

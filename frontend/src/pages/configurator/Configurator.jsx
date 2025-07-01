import './Configurator.css'
import { useState, useEffect } from 'react'

import Menu  from '@components/menu/Menu'
import Background_blur_config from '@components/background_blur_config/Background_blur_config'
import Config_home_start from '@components/config_home_start/Config_home_start'
import Config_home_calendar from '@components/config_home_calendar/Config_home_calendar'
import Config_home_history from '@components/config_home_history/Config_home_history'
import Init_personal_info from '@components/init_personal_info/Init_personal_info'
import Init_details from '@components/init_details/Init_details'
import Schedule_hours from '@components/schedule_hours/Schedule_hours'
import Schedule_days from '@components/schedule_days/Schedule_days'
import Priority_people from '@components/priority_people/Priority_people'
import Priority_hour from '@components/priority_hour/Priority_hour'
import Event_inputs from '@components/event_inputs/Event_inputs'
import Event_calendar from '@components/event_calendar/Event_calendar'
import Notifications_caption from '@components/notifications_caption/Notifications_caption'
import Notifications_heft from '@components/notifications_heft/Notifications_heft'
import Notifications_message from '@components/notifications_message/Notifications_message'

import axios from 'axios'

const Configurator = () => {
    
    const getSafeTheme = () => {
        const theme = localStorage.getItem('theme');
        return theme === "dark" || theme === "light" ? theme : "dark";
    };
    
    const [darkMode, setDarkMode] = useState(() => getSafeTheme() === "dark");
    
    useEffect(() => {
        const savedTheme = getSafeTheme();
        document.documentElement.setAttribute("data-theme", savedTheme);
        setDarkMode(savedTheme === "dark");
    }, []);

    const [onboardingStep, setOnboardingStep] = useState('consent'); // 'consent' | 'guide' | 'done'


    


    const varDic = {
        language: 'init',
        full_name: 'init',
        work_hours_from: 'schedule',
        work_hours_to: 'schedule',
      }
    

    const [flowMissingData, setFlowMissingData] = useState(null);

    const [highlightSections, setHighlightSections] = useState([]);

    const handleMissingData = (missingFields) => {
        setFlowMissingData(missingFields);

        if (missingFields && missingFields.length > 0) {
            const affectedSections = new Set();

            missingFields.forEach(field => {
                const section = varDic[field];
                if (section) affectedSections.add(section);
            });

            setHighlightSections(Array.from(affectedSections));
            setIsMenuOpen(true);
        } else {
            setHighlightSections([]);
        }
    };

    useEffect(() => {
        if (onboardingStep === 'guide') {
            setIsMenuOpen(true);
            setHighlightSections(['init', 'schedule']);
        }
        if (onboardingStep === 'done') {
            setHighlightSections([]); // Limpiar los resaltados
        }
    }, [onboardingStep]);



    // Array de las secciones abiertas / cerradas
    const [selectedSection, setSelectedSection] = useState('home');
    const [isMenuOpen, setIsMenuOpen] = useState(false);


    const safeSections = ["home", "init", "schedule", "priority", "event", "metrics", "calendar", "notify", "profile"];

    const handleSectionChange = (section) => {
        if (section === 'calendar') {
            window.open('https://calendar.google.com', '_blank');
            return;
        }
    
        if (safeSections.includes(section)) {
            setSelectedSection(section);
        }
    };
    

    const [showHeftConfig, setShowHeftConfig] = useState(false);

    const handleOpenHeft = () => {
        setShowHeftConfig(true);
    };

    const handleCloseHeft = () => {
        setShowHeftConfig(false);
    };


    const validateAndFormat = (name, value, type = "string") => {
        const formattedName = name.toLowerCase();  // Normaliza el nombre del campo
    
        if (type === "number") {
            const parsedValue = parseFloat(value);
            if (isNaN(parsedValue)) return null; // Retorna null si no es un número válido
            return { name: formattedName, value: parsedValue };
        }
    
        if (type === "string") {
            if (typeof value !== "string") return null;
            return { name: formattedName, value: value.trim() }; // Elimina espacios en blanco innecesarios
        }
    
        if (type === "array") {
            if (!Array.isArray(value)) return null;
            return { name: formattedName, value };
        }
    
        return null;
    };

    const [missingInitData, setMissingInitData] = useState({
        fullname: false,
        language: false
    });
    
    const [missingScheduleData, setMissingScheduleData] = useState({
        init_schedule: false,
        end_schedule: false
    });


    const handleSaveInit = async () => {
        const missingFields = {
          fullname: initData.fullname.trim() === "",
          language: initData.language.trim() === ""
        };
      
        setMissingInitData(missingFields);
      
        const hasMissing = Object.values(missingFields).includes(true);
        if (hasMissing) {
          return false;
        }
      
        const requestData = {
          ...initData,
          email: userData?.email
        };
      
        try {
          const response = await saveStartConfig(requestData);
          return response === true;
        } catch (err) {
          return false;
        }
      };
      
    

    const handleSaveSchedule = async () => {
        const missingFields = {
          init_schedule: scheduleData.init_schedule.trim() === "",
          end_schedule: scheduleData.end_schedule.trim() === ""
        };
      
        setMissingScheduleData(missingFields);
      
        const hasMissing = Object.values(missingFields).includes(true);
        if (hasMissing) {
          return false;
        }
      
        const requestData = {
          ...scheduleData,
          email: userData?.email
        };
      
        try {
          const response = await saveScheduleConfig(requestData);
          return response === true;
        } catch (err) {
          return false;
        }
      };
      
    
    const handleSavePriority = async () => {
        // Creamos una copia limpia
        const filteredData = {};
    
        // Recorremos los campos de priorityData
        Object.entries(priorityData).forEach(([key, value]) => {
            // Si el campo es string y no está vacío, lo incluimos
            if (typeof value === "string" && value.trim() !== "") {
                filteredData[key] = value.trim();
            }
            // Si el campo es un array y tiene elementos, lo incluimos
            else if (Array.isArray(value) && value.length > 0) {
                filteredData[key] = value;
            }
        });
    
        // Añadir email si existe
        if (userData?.email) {
            filteredData.email = userData.email;
        }
    
        await savePriorityConfig(filteredData);
    };
    
    
    const handleSaveEvent = async () => {
        const requestData = {
            ...eventData,
            email: userData?.email  
        };
    
        // console.log("Enviando datos a la API (Event):", requestData);
    
        await saveEventConfig(requestData);
    };
    
    const [initData, setInitData] = useState({
        fullname: "",
        position: "",
        language: "",
        details: ""
    });

    const [scheduleData, setScheduleData] = useState({
        init_schedule: "",
        end_schedule: "",
        init_schedule_no_meeting: "",
        end_schedule_no_meeting: "",
        days_blocked: [],
        margin_event: 0
    });

    const [priorityData, setPriorityData] = useState({
        priority_subject: "",
        priority_people: "",
        init_priority_schedule: "",
        end_priority_schedule: "",
        priority_days: []
    });

    const [eventData, setEventData] = useState({
        meeting_duration: 30,
        meeting_limit: 30,
        days_off: [],
        notify_meeting: false,
        meeting_porpose: false,
        free_days: []
    });

    const handleInitChange = (name, value) => {
        const result = validateAndFormat(name, value, "string");
        if (result) {
            setInitData(prevData => ({
                ...prevData,
                [result.name]: result.value
            }));
        }
    };
    
    const handleScheduleChange = (name, value) => {
        if (name === "days_blocked") {
            // Se asume que 'value' es el array final con los días seleccionados
            setScheduleData(prevData => ({
            ...prevData,
            days_blocked: value
            }));
        } else {
            const type = ["margin_event"].includes(name) ? "number" : "string";
            const result = validateAndFormat(name, value, type);
            if (result) {
            setScheduleData(prevData => ({
                ...prevData,
                [result.name]: result.value
            }));
            }
        }
    };
      
    
    const handlePriorityChange = (name, value) => {
    if (name === "priority_days") {
        // 'value' es el array final con los días seleccionados
        setPriorityData(prevData => ({
        ...prevData,
        priority_days: value
        }));
    } else {
        const result = validateAndFormat(name, value, "string");
        if (result) {
        setPriorityData(prevData => ({
            ...prevData,
            [result.name]: result.value
        }));
        }
    }
    };
      
    const handleEventChange = (name, value, checked) => {
        // Si el valor recibido es un array (caso de checkbox-group), se asigna directamente
        if (name === "days_off" && Array.isArray(value)) {
        setEventData(prevData => ({
            ...prevData,
            days_off: value
        }));
        } else if (name === "notify_meeting" || name === "meeting_porpose") {
        setEventData(prevData => ({
            ...prevData,
            [name]: Boolean(checked)
        }));
        } else {
        const type = ["meeting_duration", "meeting_limit"].includes(name)
            ? "number"
            : "string";
        const result = validateAndFormat(name, value, type);
        if (result) {
            setEventData(prevData => ({
            ...prevData,
            [result.name]: result.value
            }));
        }
        }
    };
      
    // Manejar la selección de fechas en el calendario
    const handleDateSelection = (date) => {
        if (!(date instanceof Date) || isNaN(date)) return;
    
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        const dateStr = `${year}-${month}-${day}`;
    
        setEventData(prevData => ({
            ...prevData,
            free_days: prevData.free_days.includes(dateStr)
                ? prevData.free_days.filter(d => d !== dateStr)
                : [...prevData.free_days, dateStr]
        }));
    };
    
    // Estado para guardar los datos del usuario (por ejemplo, gmail, username, etc.)
    const [userData, setUserData] = useState(null);

    // Función para obtener los datos del usuario desde el backend
    const fetchUserData = async () => {
        try {
        const response = await axios.post('/api/user/data/', {}, { withCredentials: true });
        if (response.status === 200) {
            // Asumimos que el backend devuelve, al menos, { email, username, is_active_auto }
            const { email, username, is_active_auto, is_first_login } = response.data;
            setUserData({ email, username, is_active_auto, is_first_login });
        } else {
            // console.error('Error al obtener los datos del usuario');
            console.log("")
        }
        } catch (error) {
        // console.error('Error al procesar los datos del usuario:', error);
        console.log("")
        }
    };

    // Llamamos a fetchUserData al montar el componente
    useEffect(() => {
        if(!userData){
            fetchUserData();
        }
    }, []);

    useEffect(() => {
        if (userData?.is_first_login) {
            setOnboardingStep('consent');
        }
    }, [userData]);

    // Funciones para actualizar la configuración en el backend mediante Axios
    const saveStartConfig = async (configData) => {
        try {
          const response = await axios.post('/api/save-start-config/', configData, { withCredentials: true });
          return response.status === 200;
        } catch (error) {
          return false;
        }
      };
      

    const saveScheduleConfig = async (configData) => {
        try {
          const response = await axios.post('/api/save-schedule-config/', configData, { withCredentials: true });
          return response.status === 200;
        } catch (error) {
          return false;
        }
      };
      

    const savePriorityConfig = async (configData) => {
        try {
        const response = await axios.post('/api/save-priority-config/', configData, { withCredentials: true });
        if (response.status === 200) {
            // console.log("Priority configuration saved:", response.data);
        } else {
            // console.error("Error saving priority configuration");
            console.log("")
        }
        } catch (error) {
        // console.error("Error saving priority configuration:", error);
        console.log("")
        }
    };

    const saveEventConfig = async (configData) => {
        try {
        const response = await axios.post('/api/save-event-config/', configData, { withCredentials: true });
        if (response.status === 200) {
            // console.log("Event configuration saved:", response.data);
        } else {
            // console.error("Error saving event configuration");
            console.log("")
        }
        } catch (error) {
        // console.error("Error saving event configuration:", error);
        console.log("")
        }
    };
    
    
    const renderComponents = () => {
        switch (selectedSection) {
            case 'home':
                return (
                    <>
                      <Config_home_start userEmail={userData.email} onMissingData={handleMissingData} />
                      <Config_home_calendar />
                      <Config_home_history />
                    </>
                );
            case 'init':
                return (
                    <>
                        <Init_personal_info onChange={handleInitChange} missingData={missingInitData} />
                        <Init_details onChange={handleInitChange} onSave={handleSaveInit} />
                    </>
                );
            case 'schedule':
                return (
                    <>
                        <Schedule_hours onChange={handleScheduleChange} missingData={missingScheduleData} />
                        <Schedule_days onChange={handleScheduleChange} onSave={handleSaveSchedule} />
                    </>
                )
            case 'priority':
                return (
                    <>
                        <Priority_people onChange={handlePriorityChange}/>
                        <Priority_hour onChange={handlePriorityChange} onSave={handleSavePriority}/>
                    </>
                )
            case 'event':
                return (
                    <>
                        <Event_inputs eventData={eventData} onChange={handleEventChange} onSave={handleSaveEvent}/>
                        <Event_calendar selectedDates={eventData.free_days} onSelectDate={handleDateSelection}/>
                    </>
                )
            case 'metrics':
                return <h2>Métricas aún no implementadas</h2>;
            case 'notify':
                const isMobile = window.innerWidth <= 1024;
                
                if (isMobile && showHeftConfig) {
                    return (
                      <div className="element-space activeHeft">
                        <Notifications_heft showIcon={isMobile} onClose={handleCloseHeft} />
                      </div>
                    );
                }                   
                return (
                    <>
                    <Notifications_caption
                        showIcon={isMobile}
                        onOpenConfig={() => setShowHeftConfig(true)}
                    />
                    <Notifications_message />
                    {!isMobile && (
                        <Notifications_heft showIcon={isMobile} onClose={handleCloseHeft}/>
                    )}
                    </>
                );                  
            case 'profile':
                return <h2>Perfil de usuario</h2>;
            default:
                return <h2>Selecciona una opción del menú</h2>;
        }
    };

    if (!userData) {
        return (
            <div className="dot-container">
                {[...Array(16)].map((_, i) => <div key={i} className="dot"></div>)}
            </div>
        );
    }

    return (
        <>
            {/* Onboarding Overlay */}
            {userData?.is_first_login && onboardingStep !== 'done' && (
                <div className={`onboarding-overlay ${onboardingStep}`}>
                    {onboardingStep === 'consent' && (
                        <div className="onboarding-box o-b-advise">
                            <h2>Consentimiento para el uso de IA</h2>
                            <p>
                                Este sistema analiza tus correos y calendario mediante una API de terceros (OpenAI) con cifrado TLS.
                                ¿Aceptas que tus correos y datos sean procesados para ofrecerte asistencia automatizada?
                            </p>
                            <div className="onboarding-buttons">
                                <button
                                    onClick={async () => {
                                        setOnboardingStep('guide');
                                    }}
                                >Acepto</button>
                                <button onClick={() => window.location.href = '/'}>No acepto</button>
                            </div>
                        </div>
                    )}
                    {onboardingStep === 'guide' && (
                        <div className="onboarding-box o-b-guide">
                            <h2>Guía de configuración</h2>
                            <p>
                                Para poder utilizar AISERV, debes completar los campos obligatorios resaltados en las secciones del menú.
                            </p>
                            <button
                                onClick={() => {
                                    setOnboardingStep('done');
                                    axios.post('/api/onboarding/complete/', {}, { withCredentials: true });
                                }}
                            >Entendido</button>
                        </div>
                    )}
                </div>
            )}

            {/* Interfaz principal */}
            <section className="configurator">
                <Background_blur_config />
                <Menu setSelectedSection={handleSectionChange} isMenuOpen={isMenuOpen} setIsMenuOpen={setIsMenuOpen} highlightSections={highlightSections} />
                <div className={`element-space ${isMenuOpen ? 'pushed' : ''} 
                    ${selectedSection === 'init' ? 'initOpen' : ''} 
                    ${selectedSection === 'schedule' ? 'scheduleOpen' : ''} 
                    ${selectedSection === 'priority' ? 'priorityOpen' : ''} 
                    ${selectedSection === 'event' ? 'eventOpen' : ''}
                    ${selectedSection === 'notify' && !showHeftConfig ? 'notifyOpen' : ''}
                    ${selectedSection === 'notify' && showHeftConfig ? 'activeHeft' : ''}
                    `}>
                    {renderComponents()}
                </div>
            </section>
        </>
    );

}

export default Configurator

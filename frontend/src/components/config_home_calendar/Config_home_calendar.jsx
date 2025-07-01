import { useState, useEffect, useMemo, useCallback, useRef } from 'react';
import axios from 'axios';
import './Config_home_calendar.css';

// Sanitización de texto para prevenir XSS
const sanitizeText = (text) => {
    if (typeof text !== 'string') return '';
    return text.replace(/[<>"/'`]/g, '');
};

// Funciones para cifrar y descifrar datos en localStorage
const encryptData = (data) => btoa(unescape(encodeURIComponent(JSON.stringify(data))));
const decryptData = (data) => {
    try {
        return JSON.parse(decodeURIComponent(escape(atob(data))));
    } catch (error) {
        return [];
    }
};

const ConfigHomeCalendar = () => {
    const [dateTime, setDateTime] = useState({
        month: '',
        number: '',
        day: '',
        hour: ''
    });

    const [events, setEvents] = useState([]);
    const cacheRef = useRef({});
    const lastUpdateRef = useRef(null);

    useEffect(() => {
        const updateDateTime = () => {
            const now = new Date();
            setDateTime({
                month: now.toLocaleDateString('es-ES', { month: 'long' }),
                number: now.getDate(),
                day: now.toLocaleDateString('es-ES', { weekday: 'long' }),
                hour: now.toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
            });
        };

        updateDateTime();
        const intervalId = setInterval(updateDateTime, 1000);
        return () => clearInterval(intervalId);
    }, []);

    const fetchEvents = useCallback(async () => {
        const today = new Date().toISOString().split('T')[0];
        const cacheKey = `events_${today}`;
        const cacheTimestampKey = `events_timestamp`;
        const cacheTTL = 1 * 60 * 1000; // 5 minutos
        

        // Verificar si la caché es válida
        const lastCacheUpdate = parseInt(localStorage.getItem(cacheTimestampKey), 10) || 0;
        if (Date.now() - lastCacheUpdate < cacheTTL) {
            const cachedData = localStorage.getItem(cacheKey);
            if (cachedData) {
                const decryptedEvents = decryptData(cachedData);
                // console.log("Eventos cargados de cache:", newEvents);
                setEvents(decryptedEvents);
                cacheRef.current[today] = decryptedEvents;
                return;
            }
        }

        try {

            const response = await axios.get(
                '/api/get-calendar-events/',
                { withCredentials: true }
            );
            // console.log("Respuesta cruda de backend:", response.data);


            const newEvents = response.data.events || [];

            // console.log("Eventos nuevos:", newEvents);
            

            // Validar cambios en caché antes de actualizar
            const cached = cacheRef.current[today] || [];
            // console.log("Eventos en caché:", cached);
            if (JSON.stringify(newEvents) !== JSON.stringify(cached)) {
                setEvents(newEvents);
                // console.log("Eventos cargados:", newEvents);
                cacheRef.current[today] = newEvents;
                localStorage.setItem(cacheKey, encryptData(newEvents));
                localStorage.setItem(cacheTimestampKey, Date.now().toString());
                lastUpdateRef.current = new Date();
            } else {
                // console.log("Fuera del if")
            }

        } catch (error) {
            // console.error(' Error obteniendo eventos:', error.response?.data?.error || error.message);
            // console.log("Error",error)
        }
    }, []);

    useEffect(() => {
        fetchEvents();
        const interval = setInterval(fetchEvents, 20000);
        return () => clearInterval(interval);
    }, [fetchEvents]);

    const hourWindow = useMemo(() => {
        const hours = [];
        const now = new Date();
        const startHour = now.getHours() - 1;
        const endHour = now.getHours() + 4;

        for (let i = startHour; i <= endHour; i++) {
            hours.push(((i + 24) % 24).toString().padStart(2, '0') + ':00');
        }

        return hours;
    }, []);

    const eventsForToday = useMemo(() => {
        const today = new Date().toISOString().split('T')[0];
        return events.filter(event => {
            const eventDate = event.start.dateTime
                ? event.start.dateTime.split('T')[0]
                : event.start.date;
            return eventDate === today;
        }).sort((a, b) => new Date(a.start.dateTime) - new Date(b.start.dateTime));
    }, [events]);

    return (
        <div className="calendar-home-square">
            <h1>Calendario</h1>
            <div className="calendar-cont-all">

                <div className="calendar-day">
                    <div className="day-cont">
                        <p className="month">{sanitizeText(dateTime.month)}</p>
                        <h2 className="number">{dateTime.number}</h2>
                        <p className="day">{sanitizeText(dateTime.day)}</p>
                        <h3 className="hour">{sanitizeText(dateTime.hour)}</h3>
                    </div>
                </div>
                
                <div className="calendar-sch">
                    <div className="sch-cont">
                        {hourWindow.map((hour, index) => {
                            const eventsInHour = eventsForToday.filter(event => {
                                const eventStartTime = new Date(event.start.dateTime);
                                return eventStartTime.getHours() === parseInt(hour.split(':')[0], 10);
                            });

                            return (
                                <div key={index} className="hour-slot">
                                    <strong className="hour-label">{hour}</strong>
                                    {eventsInHour.map((event, idx) => {
                                        const eventStartTime = new Date(event.start.dateTime);
                                        const eventEndTime = new Date(event.end.dateTime);

                                        const startMinutes = eventStartTime.getMinutes();
                                        const duration = (eventEndTime - eventStartTime) / (1000 * 60);

                                        const topOffset = (startMinutes / 60) * 100;
                                        const eventHeight = (duration / 60) * 100;

                                        const eventWidth = 90 / eventsInHour.length; 
                                        const eventLeft = 10 + idx * eventWidth; 

                                        return (
                                            <div
                                                key={idx}
                                                className="event"
                                                style={{
                                                    top: `${topOffset}%`,
                                                    height: `${eventHeight}%`,
                                                    position: 'absolute',
                                                    left: `${eventLeft}%`,
                                                    width: `${eventWidth}%`
                                                }}
                                            >
                                                <span>{sanitizeText(event.summary)}</span>
                                                <br />
                                                <small>
                                                    {eventStartTime.toLocaleTimeString('es-ES', {
                                                        hour: '2-digit',
                                                        minute: '2-digit',
                                                    })} - {eventEndTime.toLocaleTimeString('es-ES', {
                                                        hour: '2-digit',
                                                        minute: '2-digit',
                                                    })}
                                                </small>
                                            </div>
                                        );
                                    })}
                                </div>
                            );
                        })}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ConfigHomeCalendar;

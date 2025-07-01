import React, { useEffect, useRef, useState } from 'react';
import axios from 'axios';
import './Notifications_message.css';
import NotificationItem from '@components/notification_item/Notification_item';
import Notifications_heft from '@components/notifications_heft/Notifications_heft'; // si usas este componente aquí

const NotificationsMessage = () => {
  const [notifications, setNotifications] = useState([]);
  const [priorityData, setPriorityData] = useState({
    notification_low: [],
    notification_moderate: [],
    notification_high: [],
    notification_urgent: [],
  });
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const socketRef = useRef(null);

  // Cargar caché y primera página
  useEffect(() => {
    const cached = localStorage.getItem("cachedNotifications");
    const cachedMore = localStorage.getItem("hasMore");

    if (cached) setNotifications(JSON.parse(cached));
    if (cachedMore !== null) setHasMore(JSON.parse(cachedMore));

    fetchNotifications(1);
    fetchPriorities(); // también al montar
  }, []);

  // WebSocket en tiempo real
  useEffect(() => {
    // socketRef.current = new WebSocket("ws://localhost:8000/ws/notificaciones/");
    const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
    const host = window.location.host; // www.aiserv.es
    socketRef.current = new WebSocket(`${protocol}://${host}/ws/notificaciones/`);

    const socket = socketRef.current;

    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.value === true) {
          fetchNotifications(1);
          setPage(1);
        }
      } catch (e) {
        console.log("");
      }
    };

    return () => {
      if (socketRef.current) socketRef.current.close();
    };
  }, []);

  // Obtener notificaciones
  const fetchNotifications = async (pageNumber) => {
    try {
      const response = await axios.get(`/api/get-notifications?page=${pageNumber}`, {
        withCredentials: true,
      });

      if (response.status === 200) {
        const { results, next } = response.data;
        const updatedNotifications = pageNumber === 1
          ? results
          : [...notifications, ...results];

        setNotifications(updatedNotifications);
        setHasMore(!!next);
        setPage(pageNumber);

        localStorage.setItem("cachedNotifications", JSON.stringify(updatedNotifications));
        localStorage.setItem("hasMore", JSON.stringify(!!next));
      }
    } catch (error) {
      console.log("");
    }
  };

  // Obtener configuración de prioridad
  const fetchPriorities = async () => {
    try {
      const response = await axios.get('/api/get-priority-notifications/', {
        withCredentials: true,
      });
      setPriorityData(response.data);
    } catch (error) {
      // console.log("Error al cargar prioridades");
    }
  };

  // Callback para actualizar prioridades desde Notifications_heft
  const handlePriorityChange = () => {
    fetchPriorities();
  };

  const loadMore = () => {
    if (hasMore) {
      const nextPage = page + 1;
      fetchNotifications(nextPage);
    }
  };

  return (
    <div className="notification-message-square">
      <div className="notification-message-square-cont">
        {notifications.length === 0 ? (
          <p className="no-notifications">Actualmente no tienes notificaciones.</p>
        ) : (
          <>
            {notifications.map((notif) => (
              <NotificationItem
                key={notif.id || notif.title + notif.sent_date}
                notification={notif}
                priorityData={priorityData}
              />
            ))}
            {hasMore && (
              <button onClick={loadMore} className="load-more">Cargar más</button>
            )}
          </>
        )}
      </div>
    </div>
  );
  
};

export default NotificationsMessage;

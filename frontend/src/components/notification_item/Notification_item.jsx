import "./Notification_item.css";
import Notifications_icon from '@components/notification_icon/Notification_icon';

const NotificationItem = ({ notification, priorityData }) => {
  const getColorByPriority = (level) => {
    switch (level) {
      case "Baja":
        return "#4CAF50";
      case "Moderada":
        return "#FFC107";
      case "Alta":
        return "#FF9800";
      case "Urgente":
        return "#F44336";
      default:
        return "#9E9E9E";
    }
  };

  const getTypeText = (type) => {
    switch (type) {
      case "new_event":
        return "Tienes una nueva reunión";
      case "meeting_invitation":
        return "Te han invitado a una reunión";
      case "change_event":
        return "Se ha cambiado la fecha de una reunión";
      case "cancel_event":
        return "Se ha cancelado una reunión";
      case "doubt":
        return "Tienes una duda pendiente";
      case "decline_event":
        return "Han rechazado tu invitación a una reunión";
      case "confirm_event":
        return "Se ha confirmado una reunión";
      default:
        return "Notificación";
    }
  };

  // Clasificación de prioridad según datos pasados desde el padre
  const matchLevel = (value) => {
    if (priorityData.notification_low?.includes(value)) return "Baja";
    if (priorityData.notification_moderate?.includes(value)) return "Moderada";
    if (priorityData.notification_high?.includes(value)) return "Alta";
    if (priorityData.notification_urgent?.includes(value)) return "Urgente";
    return "Sin clasificar";
  };

  const priorityTypeLevel = matchLevel(notification.type);
  const priorityLabelLevel = matchLevel(notification.label);

  const colorEtiqueta = getColorByPriority(priorityLabelLevel);
  const colorTipo = getColorByPriority(priorityTypeLevel);
  const typeText = getTypeText(notification.type);

  // Formatear fecha: ejemplo "23 abr, 14:18"
  const formatDate = (isoString) => {
    if (!isoString) return "";
    const date = new Date(isoString);
    if (isNaN(date)) return "Fecha inválida";
  
    const day = date.getDate().toString().padStart(2, '0');
    const month = (date.getMonth() + 1).toString().padStart(2, '0');
    const hour = date.getHours().toString().padStart(2, '0');
    const minute = date.getMinutes().toString().padStart(2, '0');
  
    return `${day}/${month}, ${hour}:${minute}`;
  };
  

  const formattedTime = formatDate(notification.sent_date);

  return (
    <div className="notification-item">
      <div className="notification-content">
        <p className="notification-title"><strong>{notification.title}</strong></p>
        <p className="notification-body">{notification.body}</p>
        <p className="notification-hour">{formattedTime}</p>
      </div>

      <div className="notification-icons">
        <div className="notification-icon-item">
          <Notifications_icon color={colorEtiqueta} />
          <p className="notification-sender" style={{ color: colorEtiqueta }}>
            {notification.sender}
          </p>
        </div>
        <div className="notification-icon-item">
          <Notifications_icon color={colorTipo} />
          <p className="notification-type" style={{ color: colorTipo }}>
            {typeText}
          </p>
        </div>
      </div>
    </div>
  );
};

export default NotificationItem;

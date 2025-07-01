import React, { useState, useEffect } from 'react';
import './Notifications_heft.css';
import Notifications_icon from '@components/notification_icon/Notification_icon';
import axios from 'axios';

const Notifications_heft = ({ showIcon, onClose, onPriorityConfigChange }) => {
  const colorMap = {
    green: '#4CAF50',
    yellow: '#FFC107',
    orange: '#FF9800',
    red: '#F44336',
  };

  const backgroundMap = {
    green: '#4caf4f36',
    yellow: '#FFC10736',
    orange: '#FF980036',
    red: '#F4433636',
  };

  const labelMap = {
    confirm_event: "Confirmación de reunión",
    new_event: "Nueva reunión",
    change_event: "Cambio de reunión",
    cancel_event: "Cancelación de reunión",
    decline_event: "Rechazo de reunión",
    meeting_invitation: "Invitación a reunión",
    doubt: "Duda",
    // Otros como "compañero", "cliente importante", etc., se mantienen tal cual
  };

  const buildColumn = (colorKey, items) => ({
    id: colorKey,
    color: colorMap[colorKey],
    backgroundColor: backgroundMap[colorKey],
    title: <Notifications_icon color={colorMap[colorKey]} />,
    items: items.map((raw, idx) => ({
      id: `${colorKey}-${idx}`,
      text: labelMap[raw] || raw,
      raw: raw,
    })),
  });

  const [labels, setLabels] = useState({});
  const [actions, setActions] = useState({});

  useEffect(() => {
    const fetchPriorityConfig = async () => {
      try {
        const response = await axios.get('/api/get-priority-notifications/', {
          withCredentials: true,
        });

        const data = response.data;
        const labelKeys = ['compañero', 'nuevo cliente', 'cliente importante', 'superior'];

        const buildFilteredColumn = (colorKey, items) => {
          const filtered = items.filter(item => labelKeys.includes(item));
          return buildColumn(colorKey, filtered);
        };

        const buildFilteredActions = (colorKey, items) => {
          const filtered = items.filter(item => !labelKeys.includes(item));
          return buildColumn(colorKey, filtered);
        };

        setLabels({
          green: buildFilteredColumn('green', data.notification_low || []),
          yellow: buildFilteredColumn('yellow', data.notification_moderate || []),
          orange: buildFilteredColumn('orange', data.notification_high || []),
          red: buildFilteredColumn('red', data.notification_urgent || []),
        });

        setActions({
          green: buildFilteredActions('green', data.notification_low || []),
          yellow: buildFilteredActions('yellow', data.notification_moderate || []),
          orange: buildFilteredActions('orange', data.notification_high || []),
          red: buildFilteredActions('red', data.notification_urgent || []),
        });

      } catch (error) {
        console.log("");
      }
    };

    fetchPriorityConfig();
  }, []);

  const updateBackendPriorityConfig = async (updatedData) => {
    try {
      await axios.post("/api/update-priority-config/", updatedData, {
        withCredentials: true,
      });

      // Avisar al componente padre que hay una nueva configuración
      if (onPriorityConfigChange) {
        onPriorityConfigChange();
      }
    } catch (error) {
      console.log("");
    }
  };

  const onDragOver = (e) => {
    e.preventDefault();
  };

  const onLabelsDragStart = (e, fromColumnId, itemId) => {
    e.dataTransfer.setData('labelsFromColumnId', fromColumnId);
    e.dataTransfer.setData('labelsItemId', itemId);
  };

  const onLabelsDrop = (e, toColumnId) => {
    const fromColumnId = e.dataTransfer.getData('labelsFromColumnId');
    const itemId = e.dataTransfer.getData('labelsItemId');

    if (!fromColumnId || !itemId || fromColumnId === toColumnId) return;

    const sourceColumn = labels[fromColumnId];
    const targetColumn = labels[toColumnId];

    const itemIndex = sourceColumn.items.findIndex((item) => item.id === itemId);
    if (itemIndex < 0) return;

    const itemToMove = sourceColumn.items[itemIndex];
    const newSourceItems = [...sourceColumn.items];
    newSourceItems.splice(itemIndex, 1);
    const newTargetItems = [...targetColumn.items, itemToMove];

    const updatedLabels = {
      ...labels,
      [fromColumnId]: { ...sourceColumn, items: newSourceItems },
      [toColumnId]: { ...targetColumn, items: newTargetItems },
    };

    setLabels(updatedLabels);

    const updatedPayload = {
      notification_low: updatedLabels.green.items.map(i => i.raw).concat(actions.green.items.map(i => i.raw)),
      notification_moderate: updatedLabels.yellow.items.map(i => i.raw).concat(actions.yellow.items.map(i => i.raw)),
      notification_high: updatedLabels.orange.items.map(i => i.raw).concat(actions.orange.items.map(i => i.raw)),
      notification_urgent: updatedLabels.red.items.map(i => i.raw).concat(actions.red.items.map(i => i.raw)),
    };

    updateBackendPriorityConfig(updatedPayload);
  };

  const onActionsDragStart = (e, fromColumnId, itemId) => {
    e.dataTransfer.setData('actionsFromColumnId', fromColumnId);
    e.dataTransfer.setData('actionsItemId', itemId);
  };

  const onActionsDrop = (e, toColumnId) => {
    const fromColumnId = e.dataTransfer.getData('actionsFromColumnId');
    const itemId = e.dataTransfer.getData('actionsItemId');

    if (!fromColumnId || !itemId || fromColumnId === toColumnId) return;

    const sourceColumn = actions[fromColumnId];
    const targetColumn = actions[toColumnId];

    const itemIndex = sourceColumn.items.findIndex((item) => item.id === itemId);
    if (itemIndex < 0) return;

    const itemToMove = sourceColumn.items[itemIndex];
    const newSourceItems = [...sourceColumn.items];
    newSourceItems.splice(itemIndex, 1);
    const newTargetItems = [...targetColumn.items, itemToMove];

    const updatedActions = {
      ...actions,
      [fromColumnId]: { ...sourceColumn, items: newSourceItems },
      [toColumnId]: { ...targetColumn, items: newTargetItems },
    };

    setActions(updatedActions);

    const updatedPayload = {
      notification_low: labels.green.items.map(i => i.raw).concat(updatedActions.green.items.map(i => i.raw)),
      notification_moderate: labels.yellow.items.map(i => i.raw).concat(updatedActions.yellow.items.map(i => i.raw)),
      notification_high: labels.orange.items.map(i => i.raw).concat(updatedActions.orange.items.map(i => i.raw)),
      notification_urgent: labels.red.items.map(i => i.raw).concat(updatedActions.red.items.map(i => i.raw)),
    };

    updateBackendPriorityConfig(updatedPayload);
  };

  return (
    <div className="notification-heft-square">
      {showIcon && (
        <button className="close-heft-btn" onClick={onClose}>
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <line x1="18" y1="6" x2="6" y2="18" />
            <line x1="6" y1="6" x2="18" y2="18" />
          </svg>
        </button>
      )}
      <h1>Personaliza los pesos de prioridad</h1>
      <p className='p-info-heft'>Arrastra los elementos a tu gusto. Con esta acción podrás dar más peso visual a las notificaciones entrantes.</p>

      <p className="label-noti">Etiquetas:</p>
      <div className="notification-heft-columns">
        {Object.values(labels).map((column) => (
          <div
            key={column.id}
            className="notification-heft-column"
            style={{ borderColor: column.color }}
            onDragOver={onDragOver}
            onDrop={(e) => onLabelsDrop(e, column.id)}
          >
            <div className="notification-heft-header">
              <h2>{column.title}</h2>
            </div>
            <div className="notification-heft-items">
              {column.items.map((item) => (
                <div
                  key={item.id}
                  className="notification-heft-item"
                  draggable
                  onDragStart={(e) => onLabelsDragStart(e, column.id, item.id)}
                  style={{ backgroundColor: column.backgroundColor }}
                >
                  <p>{item.text}</p>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>

      <p className="label-noti">Acciones:</p>
      <div className="notification-heft-columns2">
        {Object.values(actions).map((column) => (
          <div
            key={column.id}
            className="notification-heft-column"
            style={{ borderColor: column.color }}
            onDragOver={onDragOver}
            onDrop={(e) => onActionsDrop(e, column.id)}
          >
            <div className="notification-heft-items">
              {column.items.map((item) => (
                <div
                  key={item.id}
                  className="notification-heft-item"
                  draggable
                  onDragStart={(e) => onActionsDragStart(e, column.id, item.id)}
                  style={{ backgroundColor: column.backgroundColor }}
                >
                  <p>{item.text}</p>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Notifications_heft;

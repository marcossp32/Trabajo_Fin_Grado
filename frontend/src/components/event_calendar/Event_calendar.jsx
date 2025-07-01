import React from 'react';
import Calendar from 'react-calendar';
import 'react-calendar/dist/Calendar.css';
import './Event_calendar.css';

const Event_calendar = ({ selectedDates, onSelectDate }) => {
  return (
    <div className="event-calendar-square">
      <h1>Días libres</h1>
      <p>Indica tus días libres del mes</p>
      <Calendar
        onClickDay={onSelectDate}
        tileClassName={({ date, view }) => {
          if (view === 'month') {
            // 🔹 Convertimos la fecha a YYYY-MM-DD sin UTC
            const year = date.getFullYear();
            const month = String(date.getMonth() + 1).padStart(2, '0');
            const day = String(date.getDate()).padStart(2, '0');
            const dateStr = `${year}-${month}-${day}`;

            return selectedDates.includes(dateStr) ? 'selected-day' : null;
          }
        }}
      />
    </div> 
  );
};

export default Event_calendar;

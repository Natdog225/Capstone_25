import React from 'react';
import { X } from 'lucide-react';
import './CSS/EventsModal.css';

const EventsModal = ({ events, isOpen, onClose }) => {
  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Upcoming Events (Next 60 Days)</h2>
          <button className="modal-close" onClick={onClose}>
            <X size={24} />
          </button>
        </div>
        <div className="modal-body">
          <div className="events-list">
            {events.map((event) => (
              <div key={event.id} className="event-item">
                <div className="event-date">{event.date}</div>
                <div className="event-details">
                  <span className="event-name">{event.event}</span>
                  {event.subDetails && (
                    <span className="event-sub-details">{event.subDetails}</span>
                  )}
                  <span className={`event-importance ${event.importance}`}>
                    {event.importance}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
        <div className="modal-footer">
          <button className="modal-back-btn" onClick={onClose}>Back</button>
        </div>
      </div>
    </div>
  );
};

export default EventsModal;
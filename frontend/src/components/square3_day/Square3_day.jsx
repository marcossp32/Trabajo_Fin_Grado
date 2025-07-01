import './Square3_day.css';

const Square3_day = () => {
  return (
    <div className="square3">
      <div className="day">
        <p className="number-week">8</p>
        <p className="day-week">Jue</p>
      </div>
      <div className="info-square3">
        <h3>Jueves</h3>
        <div className="info-square3-hour">
          {/* icon666.com - MILLIONS vector ICONS FREE */}
          <svg
            version="1.1"
            id="Capa_1"
            x="0px"
            y="0px"
            viewBox="0 0 512 512"
            style={{ enableBackground: "new 0 0 512 512" }}
          >
            <g>
              <g>
                <path d="M377,240H272V135c0-8.284-6.716-15-15-15s-15,6.716-15,15v120c0,8.284,6.716,15,15,15h120c8.284,0,15-6.716,15-15 S385.284,240,377,240z"></path>
              </g>
            </g>
            <g>
              <g>
                <path d="M257,0C117.105,0,0,113.025,0,255c0,140.644,115.914,257,257,257c142.13,0,255-117.257,255-257 C512,114.061,397.951,0,257,0z M257,482.2C131.832,482.2,29.8,380.168,29.8,255C29.8,130.935,131.832,29.8,257,29.8 c124.065,0,225.2,101.135,225.2,225.2C482.2,380.168,381.065,482.2,257,482.2z"></path>
              </g>
            </g>
          </svg>
          <p>10:00 -</p>
          <svg
            version="1.1"
            id="Capa_1"
            x="0px"
            y="0px"
            viewBox="0 0 512 512"
            style={{ enableBackground: "new 0 0 512 512" }}
          >
            <g>
              <g>
                <path d="M377,240H272V135c0-8.284-6.716-15-15-15s-15,6.716-15,15v120c0,8.284,6.716,15,15,15h120c8.284,0,15-6.716,15-15 S385.284,240,377,240z"></path>
              </g>
            </g>
            <g>
              <g>
                <path d="M257,0C117.105,0,0,113.025,0,255c0,140.644,115.914,257,257,257c142.13,0,255-117.257,255-257 C512,114.061,397.951,0,257,0z M257,482.2C131.832,482.2,29.8,380.168,29.8,255C29.8,130.935,131.832,29.8,257,29.8 c124.065,0,225.2,101.135,225.2,225.2C482.2,380.168,381.065,482.2,257,482.2z"></path>
              </g>
            </g>
          </svg>
          <p>11:00</p>
        </div>
        <div className="info-square3-button">
          <p style={{ backgroundColor: "#a4d68e" }}>Aceptar</p>
          <p style={{ backgroundColor: "rgba(167, 167, 167, 0.46)" }}>Rechazar</p>
        </div>
      </div>
    </div>
  );
};

export default Square3_day;

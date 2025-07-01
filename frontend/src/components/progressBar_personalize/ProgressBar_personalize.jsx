import './ProgressBar_personalize.css'

const ProgressBar_personalize = ({ progress, total }) => {
    return (
      <div className="progress-container">
        <div className="progress-bar"></div>
        <span className="progress-text">{`${progress} / ${total} completado`}</span>
      </div>
    );
};

export default ProgressBar_personalize
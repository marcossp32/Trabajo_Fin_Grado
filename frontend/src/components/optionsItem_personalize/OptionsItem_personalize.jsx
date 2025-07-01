import './OptionsItem_personalize.css'

const OptionsItem_personalize = ({ label, completed }) => {
    return (
      <li className={completed ? "completed" : ""}>
        <div className="circle-list">
          {completed && <span className="tick">&#10003;</span>}
        </div>
        <label>{label}</label>
        <span className="arrow-personalize">&gt;</span>
      </li>
    );
};


export default OptionsItem_personalize
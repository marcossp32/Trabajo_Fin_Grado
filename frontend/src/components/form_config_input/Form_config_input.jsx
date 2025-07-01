import './Form_config_input.css';
import { useState } from 'react';

const Form_config_input = ({
  label,
  placeholder,
  name,
  type, 
  options = [],
  fullWidth = false,
  onChange,
  checked,
  error, // Nueva prop para marcar errores
  required
}) => {
  const [selectedValues, setSelectedValues] = useState([]);

  const handleChange = (event) => {
    const { type: inputType, value, checked: inputChecked } = event.target;
    
    if (type === "checkbox-group") {
      const newValues = inputChecked 
        ? [...selectedValues, value] 
        : selectedValues.filter(v => v !== value);
      setSelectedValues(newValues);
      onChange(name, newValues);
    } else if (type === "checkbox") {
      onChange(name, null, inputChecked);
    } else {
      onChange(name, value);
    }
  };

  return (
    <div className={`input-group ${fullWidth ? "full-width" : ""}`}>
      {type === "checkbox-group" ? (
        <>
          <label>
            {label}
            {required && <span className="required-asterisk"> *</span>}
          </label>
          <div className="checkbox-group">
            {options.map((option, index) => (
              <label key={index} className="checkbox-label">
                <input
                  type="checkbox"
                  name={name}
                  value={option.value}
                  checked={selectedValues.includes(option.value)}
                  onChange={handleChange}
                  className={error ? "input-error" : ""}
                />
                <span>{option.label}</span>
              </label>
            ))}
          </div>
        </>
      ) : type === "checkbox" ? (
        <label className="single-checkbox">
          <input
            type="checkbox"
            id={name}
            name={name}
            checked={checked}
            onChange={handleChange}
            className={error ? "input-error" : ""}
          />{" "}
          {label}
        </label>
      ) : type === "textarea" ? (
        <>
          <label>
            {label}
            {required && <span className="required-asterisk"> *</span>}
          </label>
          <textarea
            id={name}
            name={name}
            placeholder={placeholder}
            onChange={handleChange}
            className={error ? "input-error" : ""}
          ></textarea>
        </>
      ) : type === "option" ? (
        <>
          <label>
            {label}
            {required && <span className="required-asterisk"> *</span>}
          </label>
          <select
            id={name}
            name={name}
            onChange={(e) => onChange(name, e.target.value)}
            className={error ? "input-error" : ""}
          >
            <option value="">Selecciona una opción</option>
            {options.map((option, index) => (
              <option key={index} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </>
      ) : (
        <>
          <label>
            {label}
            {required && <span className="required-asterisk"> *</span>}
          </label>
          <input
            type={type}
            id={name}
            name={name}
            placeholder={placeholder}
            onChange={handleChange}
            className={error ? "input-error" : ""}
          />
        </>
      )}
    </div>
  );
};

export default Form_config_input;

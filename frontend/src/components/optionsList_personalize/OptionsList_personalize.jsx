import './OptionsList_personalize.css'

import OptionItem from '@components/optionsItem_personalize/OptionsItem_personalize'

const OptionsList_personalize = () => {
    const options = [
      { label: "Horario", completed: true },
      { label: "Prioridad", completed: true },
      { label: "Eventos", completed: false },
      { label: "Otro", completed: false },
    ];
  
    return (
      <ul className="options-list">
        {options.map((option, index) => (
          <OptionItem key={index} {...option} />
        ))}
      </ul>
    );
};

export default OptionsList_personalize


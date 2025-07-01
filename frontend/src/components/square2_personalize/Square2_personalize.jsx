import './Square2_personalize.css'

import ProgressBar from '@components/progressBar_personalize/ProgressBar_personalize'
import OptionsList from '@components/optionsList_personalize/OptionsList_personalize'

const Square2_personalize = () => {
    return (
      <div className="square2">
        <p>Configúralo</p>
        <ProgressBar progress={2} total={5} />
        <OptionsList />
      </div>
    );
};

export default Square2_personalize

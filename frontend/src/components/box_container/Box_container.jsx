import React, { forwardRef } from 'react';
import './Box_container.css';

const BoxContainer = forwardRef(({ number, title, description, isActive, isOdd }, ref) => {
  return (
    <div ref={ref} className={`box-containers ${ isOdd ? 'box-containers1' : 'box-containers2' } ${isActive ? 'active' : ''}`} >
      <div className="left-box">
        <div className="box-title">
          <h1>{title}</h1>
        </div>
        <div className="box-number">
          <p>{number}</p>
        </div>
        
      </div>
      <div className="right-box">
        <div className="box-info">
          <p>{description}</p>
        </div>
      </div>
    </div>
  );
});

export default BoxContainer;

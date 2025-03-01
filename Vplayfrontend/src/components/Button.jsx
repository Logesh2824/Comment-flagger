import React, { Fragment } from 'react';
import './button.css'; // Assuming the CSS you provided is in this file

const Button = ({ as: Component = 'button', children, filled, secondary, ...rest }) => {
  return (
    <Component
      className={`dir-control ${secondary ? 'dir-control--secondary' : ''} ${filled ? 'dir-control--filled' : ''}`}
      {...rest}
    >
      {children}
      <span />
      <span />
      <span />
      <span />
      <b aria-hidden="true">{children}</b>
      <b aria-hidden="true">{children}</b>
      <b aria-hidden="true">{children}</b>
      <b aria-hidden="true">{children}</b>
    </Component>
  );
};

export default Button; // Exporting Button instead of App

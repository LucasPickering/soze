import PropTypes from 'prop-types';
import React from 'react';

import MenuItem from '@material-ui/core/MenuItem';
import Select from '@material-ui/core/Select';

const ColorPicker = ({ color, setColor }) => (
  <Select value={color} onChange={setColor}>
    <MenuItem value="0x000000">Black</MenuItem>
    <MenuItem value="0xff0000">Red</MenuItem>
    <MenuItem value="0x00ff00">Green</MenuItem>
    <MenuItem value="0x0000ff">Blue</MenuItem>
  </Select>
);

ColorPicker.propTypes = {
  color: PropTypes.string.isRequired,
  setColor: PropTypes.func.isRequired,
};

export default ColorPicker;

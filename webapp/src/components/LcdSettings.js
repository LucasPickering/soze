import PropTypes from 'prop-types';
import React from 'react';

import FormControl from '@material-ui/core/FormControl';
import FormControlLabel from '@material-ui/core/FormControlLabel';
import FormGroup from '@material-ui/core/FormGroup';
import MenuItem from '@material-ui/core/MenuItem';
import Paper from '@material-ui/core/Paper';
import Select from '@material-ui/core/Select';
import Switch from '@material-ui/core/Switch';
import Typography from '@material-ui/core/Typography';

import ColorPicker from './ColorPicker';

const LcdSettings = ({ lcd, setData }) => {
  // Have to do this to get around prettier being shitty
  const linkToLedSwitch = (
    <Switch
      checked={lcd.link_to_led}
      onChange={(e, checked) => setData('lcd.link_to_led', checked)}
    />
  );

  return (
    <Paper>
      <Typography variant="h4">LCD</Typography>
      <FormGroup>
        <FormControl>
          <Select
            value={lcd.mode}
            onChange={e => setData('lcd.mode', e.target.value)}
          >
            <MenuItem value="off">Off</MenuItem>
            <MenuItem value="clock">Clock</MenuItem>
          </Select>
        </FormControl>
        <FormControl>
          <FormControlLabel
            label="Link to LED color"
            control={linkToLedSwitch}
          />
        </FormControl>
        <FormControl disabled={lcd.link_to_led}>
          <ColorPicker
            color={lcd.color}
            setColor={color => setData('lcd.color', color)}
          />
        </FormControl>
      </FormGroup>
    </Paper>
  );
};

LcdSettings.propTypes = {
  lcd: PropTypes.shape({
    mode: PropTypes.string.isRequired,
    color: PropTypes.string.isRequired,
    link_to_led: PropTypes.bool.isRequired,
  }).isRequired,
  setData: PropTypes.func.isRequired,
};

export default LcdSettings;

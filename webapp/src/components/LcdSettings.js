import PropTypes from 'prop-types';
import React from 'react';

import { withStyles } from '@material-ui/core/styles';
import FormControl from '@material-ui/core/FormControl';
import FormControlLabel from '@material-ui/core/FormControlLabel';
import FormGroup from '@material-ui/core/FormGroup';
import MenuItem from '@material-ui/core/MenuItem';
import Paper from '@material-ui/core/Paper';
import Select from '@material-ui/core/Select';
import Switch from '@material-ui/core/Switch';
import Typography from '@material-ui/core/Typography';

import ColorPicker from './ColorPicker';
import styles from '../styles';

const LcdSettings = ({
  classes,
  data: { mode, link_to_led: linkToLed, color },
  setData,
}) => {
  // Have to do this to get around prettier being shitty
  const linkToLedSwitch = (
    <Switch
      checked={linkToLed}
      onChange={(e, checked) => setData('lcd.link_to_led', checked)}
    />
  );

  return (
    <Paper className={classes.paper}>
      <Typography variant="h5">LCD</Typography>
      <FormGroup>
        <FormControl>
          <Select
            value={mode}
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
        <FormControl>
          <Typography>Color</Typography>
          <ColorPicker
            color={color}
            disabled={linkToLed}
            onChange={c => setData('lcd.color', c)}
          />
        </FormControl>
      </FormGroup>
    </Paper>
  );
};

LcdSettings.propTypes = {
  classes: PropTypes.shape().isRequired,
  data: PropTypes.shape({
    mode: PropTypes.string.isRequired,
    color: PropTypes.string.isRequired,
    link_to_led: PropTypes.bool.isRequired,
  }).isRequired,
  setData: PropTypes.func.isRequired,
};

export default withStyles(styles)(LcdSettings);

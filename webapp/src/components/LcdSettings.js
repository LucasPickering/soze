import PropTypes from 'prop-types';
import React from 'react';

import { withStyles } from '@material-ui/core/styles';
import FormControl from '@material-ui/core/FormControl';
import FormControlLabel from '@material-ui/core/FormControlLabel';
import MenuItem from '@material-ui/core/MenuItem';
import Paper from '@material-ui/core/Paper';
import Select from '@material-ui/core/Select';
import Switch from '@material-ui/core/Switch';
import Typography from '@material-ui/core/Typography';

import ColorPicker from './ColorPicker';

const LcdSettings = ({ classes, lcd }) => (
  <Paper className={classes.paper}>
    <Typography variant="h4">LCD</Typography>
    <FormControl>
      <Select value={lcd.mode}>
        <MenuItem value="off">Off</MenuItem>
        <MenuItem value="clock">Clock</MenuItem>
      </Select>
    </FormControl>
    <FormControl>
      <FormControlLabel
        label="Link to LED color"
        control={<Switch checked={lcd.link_to_led} value="checkedA" />}
      />
    </FormControl>
    <FormControl disabled={lcd.link_to_led}>
      <ColorPicker color={lcd.color} setColor={() => {}} />
    </FormControl>
  </Paper>
);

LcdSettings.propTypes = {
  classes: PropTypes.object.isRequired,
  lcd: PropTypes.shape({
    mode: PropTypes.string.isRequired,
    color: PropTypes.string.isRequired,
    link_to_led: PropTypes.bool.isRequired,
  }).isRequired,
};

export default LcdSettings;

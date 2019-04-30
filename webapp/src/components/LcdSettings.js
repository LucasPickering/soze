import PropTypes from 'prop-types';
import React from 'react';

import { withStyles } from '@material-ui/core/styles';
import FormControl from '@material-ui/core/FormControl';
import FormGroup from '@material-ui/core/FormGroup';
import MenuItem from '@material-ui/core/MenuItem';
import Paper from '@material-ui/core/Paper';
import Select from '@material-ui/core/Select';
import Typography from '@material-ui/core/Typography';

import ColorPicker from './ColorPicker';
import makeSettings from './makeSettings';
import styles from 'util/styles';

const LcdSettings = ({
  classes,
  data: { mode, color },
  setField,
  children,
}) => (
  <Paper className={classes.paper}>
    <Typography variant="h5">LCD</Typography>
    <FormGroup>
      <FormControl>
        <Select value={mode} onChange={e => setField('mode', e.target.value)}>
          <MenuItem value="off">Off</MenuItem>
          <MenuItem value="clock">Clock</MenuItem>
        </Select>
      </FormControl>
      <FormControl>
        <Typography>Color</Typography>
        <ColorPicker color={color} onChange={c => setField('color', c)} />
      </FormControl>
      {children}
    </FormGroup>
  </Paper>
);

LcdSettings.propTypes = {
  classes: PropTypes.shape().isRequired,
  // Passed from makeSettings
  data: PropTypes.shape({
    mode: PropTypes.string.isRequired,
    color: PropTypes.string.isRequired,
  }).isRequired,
  setField: PropTypes.func.isRequired,
  children: PropTypes.node,
};

LcdSettings.defaultProps = {
  children: null,
};

export default withStyles(styles)(
  makeSettings(LcdSettings, { endpoint: 'lcd' })
);

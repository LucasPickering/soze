import PropTypes from 'prop-types';
import React from 'react';

import { withStyles } from '@material-ui/core/styles';
import FormControl from '@material-ui/core/FormControl';
import FormGroup from '@material-ui/core/FormGroup';
import MenuItem from '@material-ui/core/MenuItem';
import Paper from '@material-ui/core/Paper';
import Select from '@material-ui/core/Select';
import Slider from '@material-ui/lab/Slider';
import Typography from '@material-ui/core/Typography';

import ColorPicker from './ColorPicker';
import ColorSeries from './ColorSeries';
import styles from '../styles';

const moreStyles = theme => ({
  ...styles(theme),
  sliderControl: {
    padding: `${theme.spacing.unit * 2}px 0px`,
  },
});

const LedSettings = ({
  classes,
  data: {
    mode,
    static: { color: staticColor },
    fade: { colors: fadeColors, fade_time: fadeTime },
  },
  setData,
}) => (
  <Paper className={classes.paper}>
    <Typography variant="h5">LED</Typography>
    <FormGroup>
      <FormControl>
        <Select
          value={mode}
          onChange={e => setData('led.mode', e.target.value)}
        >
          <MenuItem value="off">Off</MenuItem>
          <MenuItem value="static">Static</MenuItem>
          <MenuItem value="fade">Fade</MenuItem>
        </Select>
      </FormControl>
      {mode === 'static' && (
        <FormControl>
          <ColorPicker
            color={staticColor}
            onChange={c => setData('led.static.color', c)}
          />
        </FormControl>
      )}
      {mode === 'fade' && (
        <>
          <FormControl className={classes.sliderControl}>
            <Typography>Fade Time</Typography>
            <Slider
              min={1}
              max={30}
              step={1}
              value={fadeTime}
              onChange={(e, value) => setData('led.fade.fade_time', value)}
            />
          </FormControl>

          <FormControl>
            <Typography>Color Series</Typography>
            <ColorSeries
              colors={fadeColors}
              setColors={colors => setData('led.fade.colors', colors)}
            />
          </FormControl>
        </>
      )}
    </FormGroup>
  </Paper>
);

LedSettings.propTypes = {
  classes: PropTypes.shape().isRequired,
  data: PropTypes.shape({
    mode: PropTypes.string.isRequired,
    static: PropTypes.shape({
      color: PropTypes.string.isRequired,
    }).isRequired,
    fade: PropTypes.shape({
      colors: PropTypes.arrayOf(PropTypes.string.isRequired).isRequired,
      saved: PropTypes.objectOf(
        PropTypes.arrayOf(PropTypes.string.isRequired).isRequired
      ).isRequired,
      fade_time: PropTypes.number.isRequired,
    }).isRequired,
  }).isRequired,
  setData: PropTypes.func.isRequired,
};

export default withStyles(moreStyles)(LedSettings);

import PropTypes from 'prop-types';
import React from 'react';

import FormControl from '@material-ui/core/FormControl';
import FormGroup from '@material-ui/core/FormGroup';
import MenuItem from '@material-ui/core/MenuItem';
import Paper from '@material-ui/core/Paper';
import Select from '@material-ui/core/Select';
import Slider from '@material-ui/lab/Slider';
import Typography from '@material-ui/core/Typography';

import ColorPicker from './ColorPicker';

const LedSettings = ({
  data: {
    mode,
    static: { color: staticColor },
    fade: { fade_time: fadeTime },
  },
  setData,
}) => (
  <Paper>
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
        <ColorPicker
          color={staticColor}
          setColor={c => setData('led.static.color', c)}
        />
      )}
      {mode === 'fade' && (
        <>
          <Typography id="fade-time-label">Fade Time</Typography>
          <Slider
            aria-labelledby="fade-time-label"
            min={1}
            max={30}
            step={0.5}
            value={fadeTime}
            onChange={(e, value) => setData('led.fade.fade_time', value)}
          />
        </>
      )}
    </FormGroup>
  </Paper>
);

LedSettings.propTypes = {
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

export default LedSettings;

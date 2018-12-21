import PropTypes from 'prop-types';
import React from 'react';

import AddIcon from '@material-ui/icons/Add';
import ClearIcon from '@material-ui/icons/Clear';
import IconButton from '@material-ui/core/IconButton';
import List from '@material-ui/core/List';
import ListItem from '@material-ui/core/ListItem';

import ColorPicker from './ColorPicker';

const DEFAULT_COLOR = '0x000000';

const ColorSeries = React.memo(({ colors, setColors }) => (
  <List dense>
    {colors.map((color, i) => (
      <ListItem key={i}>
        <ColorPicker
          color={color}
          onChange={newColor => {
            // Replace the color at i
            const newColors = colors.slice();
            newColors[i] = newColor;
            setColors(newColors);
          }}
        />
        <IconButton
          color="primary"
          disableRipple
          onClick={() => {
            // Remove the color at i
            setColors([...colors.slice(0, i), ...colors.slice(i + 1)]);
          }}
        >
          <ClearIcon />
        </IconButton>
      </ListItem>
    ))}
    <ListItem>
      <IconButton
        aria-haspopup="true"
        color="primary"
        disableRipple
        // Add a color to the end
        onClick={() => setColors([...colors, DEFAULT_COLOR])}
      >
        <AddIcon />
      </IconButton>
    </ListItem>
  </List>
));

ColorSeries.propTypes = {
  colors: PropTypes.arrayOf(PropTypes.string.isRequired).isRequired,
  setColors: PropTypes.func.isRequired,
};

export default ColorSeries;

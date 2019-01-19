import PropTypes from 'prop-types';
import React from 'react';

import { withStyles } from '@material-ui/core/styles';
import AddIcon from '@material-ui/icons/Add';
import ClearIcon from '@material-ui/icons/Clear';
import IconButton from '@material-ui/core/IconButton';
import List from '@material-ui/core/List';
import ListItem from '@material-ui/core/ListItem';

import ColorPicker from './ColorPicker';

const DEFAULT_COLOR = '#ffffff';

const styles = theme => ({
  root: {
    display: 'flex',
    flexDirection: 'row',
    alignItems: 'center',
    width: '100%',
  },
  list: {
    display: 'flex',
    flexDirection: 'row',
    alignItems: 'center',
    overflowX: 'auto',
  },
  listItem: {
    display: 'flex',
    flexDirection: 'column',
    padding: `0px ${theme.spacing.unit}px`,
    width: 'auto',
  },
  clearButton: {
    padding: 0,
  },
  addButton: {
    marginLeft: 'auto', // Move button to the end of the box
  },
});

const ColorSeries = React.memo(({ classes, colors, setColors }) => (
  <div className={classes.root}>
    <List className={classes.list} dense>
      {colors.map((color, i) => (
        <ListItem className={classes.listItem} key={i}>
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
            className={classes.clearButton}
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
    </List>
    <IconButton
      className={classes.addButton}
      aria-haspopup="true"
      color="primary"
      disableRipple
      // Add a color to the end
      onClick={() => setColors([...colors, DEFAULT_COLOR])}
    >
      <AddIcon />
    </IconButton>
  </div>
));

ColorSeries.propTypes = {
  classes: PropTypes.shape().isRequired,
  colors: PropTypes.arrayOf(PropTypes.string.isRequired).isRequired,
  setColors: PropTypes.func.isRequired,
};

export default withStyles(styles)(ColorSeries);

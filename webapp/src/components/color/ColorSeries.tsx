import IconButton from '@material-ui/core/IconButton';
import List from '@material-ui/core/List';
import ListItem from '@material-ui/core/ListItem';
import { Theme } from '@material-ui/core/styles';
// tslint:disable-next-line:match-default-export-name
import AddIcon from '@material-ui/icons/Add';
// tslint:disable-next-line:match-default-export-name
import ClearIcon from '@material-ui/icons/Clear';
import { makeStyles } from '@material-ui/styles';
import React from 'react';
import { Color } from 'types/core';
import ColorPicker from './ColorPicker';

const DEFAULT_COLOR = '#ffffff';

const useLocalStyles = makeStyles(({ spacing }: Theme) => ({
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
    flexWrap: 'wrap',
    minHeight: 64,
  },
  listItem: {
    display: 'flex',
    flexDirection: 'column',
    padding: `0px ${spacing(0.5)}px`,
    width: 'auto',
  },
  clearButton: {
    padding: 0,
  },
  addButton: {
    // Keep at the top-right of the box
    alignSelf: 'start',
    marginLeft: 'auto',
  },
}));

interface Props {
  colors: Color[];
  setColors: (colors: Color[]) => void;
}

const ColorSeries: React.FC<Props> = React.memo(({ colors, setColors }) => {
  const localClasses = useLocalStyles();
  return (
    <div className={localClasses.root}>
      <List className={localClasses.list} dense>
        {colors.map((color, i) => (
          <ListItem className={localClasses.listItem} key={i}>
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
              className={localClasses.clearButton}
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
        className={localClasses.addButton}
        aria-haspopup="true"
        color="primary"
        disableRipple
        // Add a color to the end
        onClick={() => setColors([...colors, DEFAULT_COLOR])}
      >
        <AddIcon />
      </IconButton>
    </div>
  );
});

export default React.memo(ColorSeries);

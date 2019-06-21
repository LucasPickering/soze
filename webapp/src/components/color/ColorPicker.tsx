import { Theme, Typography } from '@material-ui/core';
import IconButton from '@material-ui/core/IconButton';
import Popover from '@material-ui/core/Popover';
import Slider from '@material-ui/lab/Slider';
import { makeStyles } from '@material-ui/styles';
import convert from 'color-convert';
import React, { useState } from 'react';
import { CompactPicker as Picker } from 'react-color';
import { Color } from 'state/types';

const COLORS: Color[] = [
  '#333333',
  '#808080',
  '#FFFFFF',
  '#FF0000',
  '#F44E3B',
  '#FE9200',
  '#FCDC00',
  '#A4DD00',
  '#68CCCA',
  '#73D8FF',
  '#AEA1FF',
  '#FDA1FF',

  '#101010',
  '#666666',
  '#B3B3B3',
  '#00FF00',
  '#D33115',
  '#E27300',
  '#FCC400',
  '#68BC00',
  '#16A5A5',
  '#009CE0',
  '#7B64FF',
  '#FA28FF',

  '#000000',
  '#4D4D4D',
  '#999999',
  '#0000FF',
  '#9F0500',
  '#C45100',
  '#FB9E00',
  '#194D33',
  '#0C797D',
  '#0062B1',
  '#653294',
  '#AB149E',
];

const useLocalStyles = makeStyles(({ spacing }: Theme) => ({
  sliderContainer: {
    width: 300,
    padding: spacing(2),
  },
}));

interface Props {
  className?: string;
  color: Color;
  disabled: boolean;
  onChange: (color: Color) => void;
}

const ColorPicker = ({ className, color, disabled, onChange }: Props) => {
  const localClasses = useLocalStyles();
  const [anchorEl, setAnchorEl] = useState<HTMLElement | undefined>(undefined);
  const [currentColor, setCurrentColor] = useState<Color>(color);
  const [hue, saturation, brightness] = convert.hex.hsv(currentColor);

  return (
    <div>
      <IconButton
        className={className}
        disabled={disabled}
        aria-haspopup="true"
        onClick={e => setAnchorEl(e.currentTarget)}
        style={disabled ? undefined : { backgroundColor: color }}
      />
      <Popover
        open={Boolean(anchorEl)}
        onClose={() => {
          onChange(currentColor);
          setAnchorEl(undefined);
        }}
        anchorEl={anchorEl}
        anchorOrigin={{
          vertical: 'bottom',
          horizontal: 'left',
        }}
        transitionDuration={100}
      >
        <div className={localClasses.sliderContainer}>
          <Picker
            color={currentColor}
            colors={COLORS}
            onChangeComplete={c => setCurrentColor(c.hex)}
          />
          <Typography variant="subtitle2">Brightness</Typography>
          <Slider
            min={0}
            max={100}
            step={1}
            valueLabelDisplay="auto"
            value={brightness}
            onChange={(e, b) =>
              setCurrentColor(
                `#${convert.hsv.hex([hue, saturation, b as number])}`
              )
            }
          />
        </div>
      </Popover>
    </div>
  );
};

ColorPicker.defaultProps = {
  disabled: false,
};

export default React.memo(ColorPicker);

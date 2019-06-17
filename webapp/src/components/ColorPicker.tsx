import IconButton from '@material-ui/core/IconButton';
import Popover from '@material-ui/core/Popover';
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

interface Props {
  className?: string;
  color: Color;
  disabled?: boolean;
  onChange: (color: Color) => void;
}

const ColorPicker: React.FC<Props> = React.memo(
  ({ className, color, disabled = false, onChange }: Props) => {
    const [anchorEl, setAnchorEl] = useState<HTMLElement | undefined>(
      undefined
    );

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
          onClose={() => setAnchorEl(undefined)}
          anchorEl={anchorEl}
          anchorOrigin={{
            vertical: 'bottom',
            horizontal: 'left',
          }}
          transitionDuration={100}
        >
          <Picker
            color={color}
            colors={COLORS}
            onChangeComplete={c => onChange(c.hex)}
          />
        </Popover>
      </div>
    );
  }
);

export default ColorPicker;

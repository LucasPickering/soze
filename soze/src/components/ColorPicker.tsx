import IconButton from '@material-ui/core/IconButton';
import Popover from '@material-ui/core/Popover';
import React, { useState } from 'react';
import { CompactPicker as Picker } from 'react-color';
import { Color } from 'util/types';

interface Props {
  className?: string;
  color: Color;
  disabled: boolean;
  onChange: (color: Color) => void;
}

const ColorPicker: React.FC<Props> = React.memo(
  ({ className, color, disabled, onChange }: Props) => {
    const [anchorEl, setAnchorEl] = useState<HTMLElement | undefined>(
      undefined
    );

    return (
      <>
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
          <Picker color={color} onChangeComplete={c => onChange(c.hex)} />
        </Popover>
      </>
    );
  }
);

export default ColorPicker;

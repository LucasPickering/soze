import { CompactPicker as Picker } from 'react-color';
import PropTypes from 'prop-types';
import React, { useState } from 'react';

import IconButton from '@material-ui/core/IconButton';
import Popover from '@material-ui/core/Popover';

const ColorPicker = React.memo(({ className, color, disabled, onChange }) => {
  const [anchorEl, setAnchorEl] = useState(null);

  return (
    <>
      <IconButton
        className={className}
        disabled={disabled}
        aria-haspopup="true"
        size="small"
        onClick={e => setAnchorEl(e.currentTarget)}
        style={disabled ? null : { backgroundColor: color }}
      />
      <Popover
        open={Boolean(anchorEl)}
        onClose={() => setAnchorEl(null)}
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
});

ColorPicker.propTypes = {
  className: PropTypes.string,
  color: PropTypes.string.isRequired,
  disabled: PropTypes.bool,
  onChange: PropTypes.func.isRequired,
};

ColorPicker.defaultProps = {
  className: null,
  disabled: false,
};

export default ColorPicker;

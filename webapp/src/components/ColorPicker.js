import { CompactPicker as Picker } from 'react-color';
import PropTypes from 'prop-types';
import React, { useState } from 'react';

import Fab from '@material-ui/core/Fab';
import Popover from '@material-ui/core/Popover';

/**
 * Convert 0x00ff00 to #00ff00.
 * @param {string} color color
 */
const fromApiFormat = color => `#${color.substring(2)}`;

/**
 * Convert #00ff00 to 0x00ff00.
 * @param {string} color color
 */
const toApiFormat = color => `0x${color.substring(1)}`;

const ColorPicker = ({ className, color, onChange }) => {
  const [anchorEl, setAnchorEl] = useState(null);
  const htmlColor = fromApiFormat(color);

  return (
    <>
      <Fab
        className={className}
        aria-haspopup="true"
        size="small"
        onClick={e => setAnchorEl(e.currentTarget)}
        style={{ backgroundColor: htmlColor }}
      >
        {''}
      </Fab>
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
        <Picker
          color={htmlColor}
          onChangeComplete={c => onChange(toApiFormat(c.hex))}
        />
      </Popover>
    </>
  );
};

ColorPicker.propTypes = {
  className: PropTypes.string,
  color: PropTypes.string.isRequired,
  onChange: PropTypes.func.isRequired,
};

ColorPicker.defaultProps = {
  className: null,
};

export default ColorPicker;

import { FormControl, Typography } from '@material-ui/core';
import ColorPicker from 'components/color/ColorPicker';
import React from 'react';
import { DataModifier, LedSettings } from 'state/types';

interface Props {
  static: LedSettings['static'];
  modifyData: DataModifier<LedSettings>;
}

const LedStaticControls: React.FC<Props> = ({
  static: { color: staticColor },
  modifyData,
}) => (
  <FormControl>
    <Typography>Color</Typography>
    <ColorPicker
      color={staticColor}
      onChange={c => {
        modifyData({
          static: {
            color: c,
          },
        });
      }}
    />
  </FormControl>
);

export default LedStaticControls;

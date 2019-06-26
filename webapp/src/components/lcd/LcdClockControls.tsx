import { FormControl, Typography } from '@material-ui/core';
import ColorPicker from 'components/color/ColorPicker';
import React from 'react';
import { Color } from 'types/core';
import { LcdSettings } from 'types/lcd';
import { DataModifier } from 'types/resource';

interface Props {
  color: Color;
  modifyData: DataModifier<LcdSettings>;
}

const LcdClockControls: React.FC<Props> = ({ color, modifyData }) => (
  <FormControl>
    <Typography>Color</Typography>
    <ColorPicker
      color={color}
      onChange={e => {
        modifyData({ color: e });
      }}
    />
  </FormControl>
);

export default LcdClockControls;

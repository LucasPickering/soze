import { FormControl, Typography } from '@material-ui/core';
import ColorPicker from 'components/color/ColorPicker';
import React from 'react';
import { DataModifier } from 'state/resource';
import { Color, LcdSettings } from 'state/types';

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

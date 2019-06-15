import { FormControl, MenuItem, Select, Typography } from '@material-ui/core';
import { capitalize } from 'lodash-es';
import React from 'react';
import { DataModifier } from 'state/resource';
import { LcdMode, LcdSettings } from 'state/types';
import ColorPicker from './ColorPicker';

interface Props {
  settings: LcdSettings;
  modifyData: DataModifier<LcdSettings>;
}

const LcdControls: React.FC<Props> = ({
  settings: { mode, color },
  modifyData,
}) => (
  <>
    <FormControl>
      <Select
        value={mode}
        onChange={e => {
          modifyData({
            mode: e.target.value as LcdMode,
          });
        }}
      >
        {Object.values(LcdMode).map(m => (
          <MenuItem key={m} value={m}>
            {capitalize(m)}
          </MenuItem>
        ))}
      </Select>
    </FormControl>
    <FormControl>
      <Typography>Color</Typography>
      <ColorPicker
        color={color}
        onChange={e => {
          modifyData({ color: e });
        }}
      />
    </FormControl>
  </>
);

export default LcdControls;

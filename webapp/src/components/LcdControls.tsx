import { FormControl, Typography } from '@material-ui/core';
import React from 'react';
import { DataModifier, LcdMode, LcdSettings } from 'state/types';
import ColorPicker from './color/ColorPicker';
import ModeSelect from './ModeSelect';

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
      <ModeSelect
        modes={Object.values(LcdMode)}
        selectedMode={mode}
        onChange={m =>
          modifyData({
            mode: m as LcdMode,
          })
        }
      />
    </FormControl>
    {mode !== LcdMode.Off && (
      <FormControl>
        <Typography>Color</Typography>
        <ColorPicker
          color={color}
          onChange={e => {
            modifyData({ color: e });
          }}
        />
      </FormControl>
    )}
  </>
);

export default LcdControls;

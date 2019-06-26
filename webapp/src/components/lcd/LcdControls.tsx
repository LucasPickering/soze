import ModeSelect from 'components/ModeSelect';
import React from 'react';
import { LcdMode, LcdSettings } from 'types/lcd';
import { DataModifier } from 'types/resource';
import LcdClockControls from './LcdClockControls';

interface Props {
  settings: LcdSettings;
  modifyData: DataModifier<LcdSettings>;
}

const LcdControls: React.FC<Props> = ({
  settings: { mode, color },
  modifyData,
}) => (
  <>
    <ModeSelect
      modes={Object.values(LcdMode)}
      selectedMode={mode}
      onChange={m =>
        modifyData({
          mode: m as LcdMode,
        })
      }
    />
    {mode !== LcdMode.Off && (
      <LcdClockControls color={color} modifyData={modifyData} />
    )}
  </>
);

export default LcdControls;

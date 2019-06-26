import ModeSelect from 'components/ModeSelect';
import React, { useMemo } from 'react';
import { LcdMode, LcdSettings } from 'types/lcd';
import { DataModifier } from 'types/resource';
import LcdClockControls from './LcdClockControls';

interface Props {
  settings: LcdSettings;
  modifyData: DataModifier<LcdSettings>;
}

const LcdControls: React.FC<Props> = React.memo(
  ({ settings: { mode, color }, modifyData }) => (
    <>
      <ModeSelect
        modes={LcdMode}
        selectedMode={mode}
        onChange={useMemo(
          () => m =>
            modifyData({
              mode: m as LcdMode,
            }),
          [modifyData]
        )}
      />
      {mode !== LcdMode.Off && (
        <LcdClockControls color={color} modifyData={modifyData} />
      )}
    </>
  )
);

export default LcdControls;

import ModeSelect from 'components/ModeSelect';
import React, { useMemo } from 'react';
import { LedMode, LedSettings } from 'types/led';
import { DataModifier } from 'types/resource';
import LedFadeControls from './LedFadeControls';
import LedStaticControls from './LedStaticControls';

interface Props {
  settings: LedSettings;
  modifyData: DataModifier<LedSettings>;
}

const LedControls: React.FC<Props> = React.memo(({ settings, modifyData }) => (
  <>
    <ModeSelect
      modes={LedMode}
      selectedMode={settings.mode}
      onChange={useMemo(
        () => m =>
          modifyData({
            mode: m as LedMode,
          }),
        [modifyData]
      )}
    />
    {settings.mode === LedMode.Static && (
      <LedStaticControls static={settings.static} modifyData={modifyData} />
    )}
    {settings.mode === LedMode.Fade && (
      <LedFadeControls fade={settings.fade} modifyData={modifyData} />
    )}
  </>
));

export default LedControls;

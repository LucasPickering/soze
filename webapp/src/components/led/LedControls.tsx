import ModeSelect from 'components/ModeSelect';
import React from 'react';
import { DataModifier, LedMode, LedSettings } from 'state/types';
import LedFadeControls from './LedFadeControls';
import LedStaticControls from './LedStaticControls';

interface Props {
  settings: LedSettings;
  modifyData: DataModifier<LedSettings>;
}

const LedControls: React.FC<Props> = ({ settings, modifyData }) => (
  <>
    <ModeSelect
      modes={Object.values(LedMode)}
      selectedMode={settings.mode}
      onChange={m =>
        modifyData({
          mode: m as LedMode,
        })
      }
    />
    {settings.mode === LedMode.Static && (
      <LedStaticControls static={settings.static} modifyData={modifyData} />
    )}
    {settings.mode === LedMode.Fade && (
      <LedFadeControls fade={settings.fade} modifyData={modifyData} />
    )}
  </>
);

export default LedControls;

import React from 'react';
import SettingsControls from './SettingsControls';

interface Props {}

const LcdControls: React.FC<Props> = ({}) => (
  <SettingsControls
    title="LCD"
    loading={false}
    modified={false}
    onApply={() => undefined}
  />
);

export default LcdControls;

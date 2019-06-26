import React from 'react';
import { LedSettings } from 'types/led';
import { DataModifier } from 'types/resource';
import FadeColorSeries from './FadeColorSeries';
import FadeTimeSlider from './FadeTimeSlider';

interface Props {
  fade: LedSettings['fade'];
  modifyData: DataModifier<LedSettings>;
}

const LedFadeControls: React.FC<Props> = React.memo(({ fade, modifyData }) => (
  <>
    <FadeTimeSlider fadeTime={fade.fade_time} modifyData={modifyData} />
    <FadeColorSeries colors={fade.colors} modifyData={modifyData} />
  </>
));

export default LedFadeControls;

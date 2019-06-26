import { FormControl, Typography } from '@material-ui/core';
import Slider from '@material-ui/lab/Slider';
import React from 'react';
import { LedSettings } from 'types/led';
import { DataModifier } from 'types/resource';

function formatSeconds(seconds: number): string {
  return `${seconds}s`;
}

interface Props {
  fadeTime: number;
  modifyData: DataModifier<LedSettings>;
}

const FadeTimeSlider: React.FC<Props> = React.memo(
  ({ fadeTime, modifyData }) => (
    <FormControl>
      <div>
        <Typography>Fade Time</Typography>
        <Slider
          min={1}
          max={30}
          step={1}
          valueLabelDisplay="auto"
          valueLabelFormat={formatSeconds}
          defaultValue={fadeTime}
          onChangeCommitted={(e, value) => {
            modifyData({
              fade: { fade_time: value as number },
            });
          }}
        />
      </div>
    </FormControl>
  )
);

export default FadeTimeSlider;

import { FormControl, Typography } from '@material-ui/core';
import Slider from '@material-ui/lab/Slider';
import ColorSeries from 'components/color/ColorSeries';
import React from 'react';
import { LedSettings } from 'state/types';
import { DataModifier } from 'state/resource';

function formatSeconds(seconds: number): string {
  return `${seconds}s`;
}

interface Props {
  fade: LedSettings['fade'];
  modifyData: DataModifier<LedSettings>;
}

const LedFadeControls: React.FC<Props> = ({ fade, modifyData }) => (
  <>
    <FormControl>
      <div>
        <Typography>Fade Time</Typography>
        <Slider
          min={1}
          max={30}
          step={1}
          valueLabelDisplay="auto"
          valueLabelFormat={formatSeconds}
          value={fade.fade_time}
          onChange={(e, value) => {
            modifyData({
              fade: {
                ...fade,
                fade_time: value as number,
              },
            });
          }}
        />
      </div>
    </FormControl>

    <FormControl>
      <Typography>Color Series</Typography>
      <ColorSeries
        colors={fade.colors}
        setColors={colors => {
          modifyData({
            fade: {
              ...fade,
              colors,
            },
          });
        }}
      />
    </FormControl>
  </>
);

export default LedFadeControls;

import { FormControl, Typography } from '@material-ui/core';
import Slider from '@material-ui/lab/Slider';
import React from 'react';
import { DataModifier, LedMode, LedSettings } from 'state/types';
import ColorPicker from './color/ColorPicker';
import ColorSeries from './color/ColorSeries';
import ModeSelect from './ModeSelect';

function formatSeconds(seconds: number): string {
  return `${seconds}s`;
}

interface Props {
  settings: LedSettings;
  modifyData: DataModifier<LedSettings>;
}

const LedControls: React.FC<Props> = ({
  settings: {
    mode,
    static: { color: staticColor },
    fade,
  },
  modifyData,
}) => (
  <>
    <FormControl>
      <ModeSelect
        modes={Object.values(LedMode)}
        selectedMode={mode}
        onChange={m =>
          modifyData({
            mode: m as LedMode,
          })
        }
      />
    </FormControl>
    {mode === LedMode.Static && (
      <FormControl>
        <Typography>Color</Typography>
        <ColorPicker
          color={staticColor}
          onChange={c => {
            modifyData({
              static: {
                color: c,
              },
            });
          }}
        />
      </FormControl>
    )}
    {mode === LedMode.Fade && (
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
    )}
  </>
);

export default LedControls;

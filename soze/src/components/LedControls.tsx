import {
  FormControl,
  MenuItem,
  Select,
  Theme,
  Typography,
} from '@material-ui/core';
import Slider from '@material-ui/lab/Slider';
import { makeStyles } from '@material-ui/styles';
import { capitalize } from 'lodash-es';
import React from 'react';
import { DataModifier } from 'state/resource';
import { LedMode, LedSettings } from 'state/types';
import ColorPicker from './ColorPicker';
import ColorSeries from './ColorSeries';

const useLocalStyles = makeStyles(({ spacing }: Theme) => ({
  sliderControl: {
    padding: `${spacing.unit * 2}px 0px`,
  },
}));

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
}) => {
  const localClasses = useLocalStyles();
  return (
    <>
      <FormControl>
        <Select
          value={mode}
          onChange={e => {
            modifyData({
              mode: e.target.value as LedMode,
            });
          }}
        >
          {Object.values(LedMode).map(m => (
            <MenuItem key={m} value={m}>
              {capitalize(m)}
            </MenuItem>
          ))}
        </Select>
      </FormControl>
      {mode === LedMode.Static && (
        <FormControl>
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
          <FormControl className={localClasses.sliderControl}>
            <Typography>Fade Time</Typography>
            <Slider
              min={1}
              max={30}
              step={1}
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
};

export default LedControls;

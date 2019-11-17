import { FormControl, Typography } from '@material-ui/core';
import { Slider } from '@material-ui/lab';
import useResource from 'hooks/useResource';
import React from 'react';
import { LedMode, LedSettings } from 'types/led';
import { Resource } from 'types/resource';
import ColorPicker from './ColorPicker';
import ColorSeries from './ColorSeries';
import ModeSelect from './ModeSelect';
import ResourceControlsContainer from './ResourceControlsContainer';

const formatSeconds = (seconds: number): string => `${seconds}s`;

const LedContainer: React.FC = () => {
  const { localData, modifyData, ...rest } = useResource<LedSettings>(
    Resource.LED
  );

  return (
    <ResourceControlsContainer title="LED" {...rest}>
      {localData && (
        <>
          <ModeSelect
            modes={LedMode}
            selectedMode={localData.mode}
            onChange={m =>
              modifyData({
                mode: m as LedMode,
              })
            }
          />
          {localData.mode === LedMode.Static && (
            <FormControl>
              <Typography>Color</Typography>
              <ColorPicker
                color={localData.static.color}
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
          {localData.mode === LedMode.Fade && (
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
                    defaultValue={localData.fade.fade_time}
                    onChangeCommitted={(e, value) => {
                      modifyData({
                        fade: { fade_time: value as number },
                      });
                    }}
                  />
                </div>
              </FormControl>
              <FormControl>
                <Typography>Color Series</Typography>
                <ColorSeries
                  colors={localData.fade.colors}
                  setColors={newColors => {
                    modifyData({
                      fade: { colors: newColors },
                    });
                  }}
                />
              </FormControl>
            </>
          )}
        </>
      )}
    </ResourceControlsContainer>
  );
};

export default LedContainer;

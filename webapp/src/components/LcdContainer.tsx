import { FormControl, Typography } from '@material-ui/core';
import useResource from 'hooks/useResource';
import React from 'react';
import { LcdMode, LcdSettings } from 'types/lcd';
import { Resource } from 'types/resource';
import ColorPicker from './ColorPicker';
import ModeSelect from './ModeSelect';
import ResourceControlsContainer from './ResourceControlsContainer';

interface Props {}

const LcdContainer: React.FC<Props> = () => {
  const { localData, modifyData, ...rest } = useResource<LcdSettings>(
    Resource.LCD
  );

  return (
    <ResourceControlsContainer title="LCD" {...rest}>
      {localData && (
        <>
          <ModeSelect
            modes={LcdMode}
            selectedMode={localData.mode}
            onChange={m =>
              modifyData({
                mode: m as LcdMode,
              })
            }
          />
          {localData.mode === LcdMode.Clock && (
            <FormControl>
              <Typography>Color</Typography>
              <ColorPicker
                color={localData.color}
                onChange={e => {
                  modifyData({ color: e });
                }}
              />
            </FormControl>
          )}
        </>
      )}
    </ResourceControlsContainer>
  );
};

export default LcdContainer;

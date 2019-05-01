import { FormControl, MenuItem, Select, Typography } from '@material-ui/core';
import React, { useContext } from 'react';
import { makeResourceKit, ResourceActionType } from 'state/resource';
import { LcdMode, LcdSettings } from 'state/types';
import makeResource from 'util/makeResource';
import ColorPicker from './ColorPicker';

const lcdResourceKit = makeResourceKit<LcdSettings>('lcd');
const {
  contexts: [StateContext, DispatchContext],
} = lcdResourceKit;

interface Props {}

const LcdControls: React.FC<Props> = ({}) => {
  const { data } = useContext(StateContext);
  const dispatch = useContext(DispatchContext);
  const { mode, color } = data!;
  return (
    <>
      <FormControl>
        <Select
          value={mode}
          onChange={e => {
            dispatch({
              type: ResourceActionType.Modify,
              value: { mode: e.target.value as LcdMode },
            });
          }}
        >
          <MenuItem value="off">Off</MenuItem>
          <MenuItem value="clock">Clock</MenuItem>
        </Select>
      </FormControl>
      <FormControl>
        <Typography>Color</Typography>
        <ColorPicker
          color={color}
          onChange={e => {
            dispatch({
              type: ResourceActionType.Modify,
              value: { color: e },
            });
          }}
        />
      </FormControl>
    </>
  );
};

export default makeResource(lcdResourceKit)(LcdControls);

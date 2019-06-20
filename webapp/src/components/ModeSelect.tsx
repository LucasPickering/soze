import { FormControl, makeStyles, MenuItem, Select } from '@material-ui/core';
import { capitalize } from 'lodash-es';
import React from 'react';

const useLocalStyles = makeStyles(() => ({
  root: {
    width: 100,
  },
}));

interface Props {
  modes: string[];
  selectedMode: string;
  onChange: (mode: string) => void;
}

const ModeSelect: React.FC<Props> = ({ modes, selectedMode, onChange }) => {
  const localClasses = useLocalStyles();
  return (
    <FormControl>
      <Select
        className={localClasses.root}
        value={selectedMode}
        onChange={e => {
          onChange(e.target.value as string);
        }}
      >
        {modes.map(mode => (
          <MenuItem key={mode} value={mode}>
            {capitalize(mode)}
          </MenuItem>
        ))}
      </Select>
    </FormControl>
  );
};

export default ModeSelect;

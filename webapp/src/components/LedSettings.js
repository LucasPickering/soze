import React, { useContext } from 'react';

import Paper from '@material-ui/core/Paper';
import Typography from '@material-ui/core/Typography';

import SozeContext from 'context/Context';

const LedSettings = () => {
  const { led } = useContext(SozeContext);
  return (
    <Paper>
      <Typography variant="h4">LED</Typography>
    </Paper>
  );
};

LedSettings.propTypes = {};

export default LedSettings;

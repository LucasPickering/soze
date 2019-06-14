import {
  Button,
  CircularProgress,
  FormGroup,
  Paper,
  Typography,
} from '@material-ui/core';
import { makeStyles } from '@material-ui/styles';
import React from 'react';

interface Props {
  title: string;
  loading: boolean;
  modified: boolean;
  saveData: () => void;
}

const Settings: React.FC<Props> = ({
  title,
  loading,
  modified,
  saveData,
  children,
}) => (
  <Paper>
    <Typography variant="h5">{title}</Typography>
    <FormGroup>
      {children}
      <Button
        variant="contained"
        color="primary"
        // Disable if loading or no modifications have been made
        disabled={loading || !modified}
        onClick={saveData}
      >
        {loading ? <CircularProgress size={21} /> : 'Apply'}
      </Button>
    </FormGroup>
  </Paper>
);

export default Settings;

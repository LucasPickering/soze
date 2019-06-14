import {
  Button,
  CircularProgress,
  FormGroup,
  Paper,
  Tab,
  Tabs,
  Typography,
} from '@material-ui/core';
import { makeStyles } from '@material-ui/styles';
import React from 'react';
import { Status } from 'state/types';

interface Props {
  title: string;
  status: Status;
  loading: boolean;
  modified: boolean;
  setStatus: (status: Status) => void;
  saveData: () => void;
}

const ResourceControlsContainer: React.FC<Props> = ({
  title,
  status,
  loading,
  modified,
  setStatus,
  saveData,
  children,
}) => (
  <Paper>
    <Typography variant="h5">{title}</Typography>
    <Tabs value={status} onChange={(e, v) => setStatus(v)}>
      {Object.values(Status).map(s => (
        <Tab key={s} value={s} label={s} />
      ))}
    </Tabs>
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

export default ResourceControlsContainer;

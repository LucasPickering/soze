import {
  AppBar,
  Button,
  CircularProgress,
  FormGroup,
  Paper,
  Tab,
  Tabs,
  Theme,
  Typography,
} from '@material-ui/core';
import { makeStyles } from '@material-ui/styles';
import React from 'react';
import { Status } from 'state/types';

const useLocalStyles = makeStyles(({ spacing, palette }: Theme) => ({
  outerContainer: {
    padding: spacing(1),
    backgroundColor: palette.background.default,
    width: 360,
  },
  innerContainer: {},
  form: {
    // Spacing between all immediate children
    '& > *': {
      margin: spacing(1),
    },
  },
}));

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
}) => {
  const localClasses = useLocalStyles();
  return (
    <Paper className={localClasses.outerContainer} elevation={2}>
      <Typography variant="h5">{title}</Typography>
      <Paper className={localClasses.innerContainer}>
        <AppBar position="static">
          <Tabs
            value={status}
            variant="fullWidth"
            onChange={(_, v) => setStatus(v)}
          >
            {Object.values(Status).map(s => (
              <Tab key={s} value={s} label={s} />
            ))}
          </Tabs>
        </AppBar>
        <FormGroup className={localClasses.form}>
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
    </Paper>
  );
};

export default ResourceControlsContainer;

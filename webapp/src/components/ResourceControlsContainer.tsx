import {
  AppBar,
  Box,
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
import { ResourceState, Status } from 'state/types';
import { isEmpty } from 'lodash-es';

const useLocalStyles = makeStyles(({ spacing, palette }: Theme) => ({
  outerContainer: {
    padding: spacing(1),
    backgroundColor: palette.background.default,
    width: 360,
  },
  innerContainer: {},
  loading: {
    padding: spacing(2),
  },
  form: {
    // Spacing between all immediate children
    '& > *': {
      margin: spacing(1),
    },
  },
  applyButton: {
    minHeight: 37, // Prevent jitter when loading icon appears
  },
}));

interface Props {
  title: string;
  state: ResourceState<any>;
  setStatus: (status: Status) => void;
  saveData: () => void;
}

const ResourceControlsContainer: React.FC<Props> = ({
  title,
  state: {
    status,
    fetch: { loading: fetchLoading },
    save: { loading: saveLoading },
    modifiedData,
  },
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
        {fetchLoading ? (
          <Box
            className={localClasses.loading}
            display="flex"
            justifyContent="center"
          >
            <CircularProgress />
          </Box>
        ) : (
          <FormGroup className={localClasses.form}>
            {children}
            <Button
              className={localClasses.applyButton}
              variant="contained"
              color="primary"
              // Disable if loading or no modifications have been made
              disabled={saveLoading || isEmpty(modifiedData)}
              onClick={saveData}
            >
              {saveLoading ? (
                <CircularProgress size={20} color="secondary" />
              ) : (
                'Apply'
              )}
            </Button>
          </FormGroup>
        )}
      </Paper>
    </Paper>
  );
};

export default ResourceControlsContainer;

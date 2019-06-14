import {
  Button,
  CircularProgress,
  FormGroup,
  Paper,
  Typography,
} from '@material-ui/core';
import { makeStyles } from '@material-ui/styles';
import { isEmpty } from 'lodash-es';
import React, { useEffect, useReducer } from 'react';
import { defaultResourceState, ResourceKit } from 'state/resource';

const useLocalStyles = makeStyles(() => ({
  root: {},
}));

interface Props {
  title: string;
  resourceKit: ResourceKit<any>;
}

const SettingsControls: React.FC<Props> = ({
  title,
  resourceKit: {
    reducer,
    fetcher,
    contexts: [StateContext, DispatchContext],
  },
  children,
}) => {
  const [state, dispatch] = useReducer(reducer, defaultResourceState);
  const { loading, status, data, modifiedData } = state;
  const loaded = Boolean(data);
  const modified = !isEmpty(modifiedData);

  // One-time data fetch
  useEffect(() => fetcher(dispatch, status), [dispatch, fetcher, status]);

  return (
    <StateContext.Provider value={state}>
      <DispatchContext.Provider value={dispatch}>
        <Paper>
          <Typography variant="h5">{title}</Typography>
          <FormGroup>
            {children}
            <Button
              variant="contained"
              color="primary"
              // Disable if loading or no modifications have been made
              disabled={loading || !modified}
              onClick={() => { }}
            >
              {loading ? <CircularProgress size={21} /> : 'Apply'}
            </Button>
          </FormGroup>
        </Paper>
      </DispatchContext.Provider>
    </StateContext.Provider>
  );
};

export default SettingsControls;

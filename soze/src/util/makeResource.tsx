import {
  Button,
  CircularProgress,
  FormGroup,
  Paper,
  Typography,
} from '@material-ui/core';
import { isEmpty } from 'lodash-es';
import { title } from 'process';
import React, { useEffect, useReducer } from 'react';
import { defaultResourceState, ResourceKit } from 'state/resource';

// This HoC wraps the component in context providers. It also wraps it in some
// visual elements common across all resources. This includes status tabs,
// the Apply button, etc.
export default function<T, Props>({
  reducer,
  fetcher,
  contexts: [StateContext, DispatchContext],
}: ResourceKit<T>): (
  Component: React.ComponentType<Props>
) => React.ComponentType<Props> {
  return Component => {
    return (props: Props) => {
      const [state, dispatch] = useReducer(reducer, defaultResourceState);
      const { loading, status, data, modifiedData } = state;
      const loaded = Boolean(data);
      const modified = !isEmpty(modifiedData);

      // One-time data fetch
      useEffect(() => fetcher(dispatch, status), [dispatch, status]);
      return (
        <StateContext.Provider value={state}>
          <DispatchContext.Provider value={dispatch}>
            <Paper>
              <Typography variant="h5">{title}</Typography>
              <FormGroup>
                {/* <Component {...props} /> */}
                <Button
                  variant="contained"
                  color="primary"
                  // Disable if loading or no modifications have been made
                  disabled={loading || !modified}
                  onClick={() => {}}
                >
                  {loading ? <CircularProgress size={21} /> : 'Apply'}
                </Button>
              </FormGroup>
            </Paper>
          </DispatchContext.Provider>
        </StateContext.Provider>
      );
    };
  };
}

import {
  Button,
  CircularProgress,
  FormGroup,
  Paper,
  Typography,
} from '@material-ui/core';
import { isEmpty } from 'lodash-es';
import React, { useEffect, useReducer } from 'react';
import { defaultResourceState, ResourceKit } from 'state/resource';

interface Props {
  title: string;
  status: string;
}

export default function<T>({
  reducer,
  fetcher,
  contexts: [StateContext, DispatchContext],
}: ResourceKit<T>): React.FC<Props> {
  const [state, dispatch] = useReducer(reducer, defaultResourceState);

  return ({ title, status, children }) => {
    const { loading, modifiedData } = state;
    const modified = !isEmpty(modifiedData);

    // One-time data fetch
    useEffect(() => fetcher(dispatch, status));

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
                onClick={() => {}} // TODO
              >
                {loading ? <CircularProgress size={21} /> : 'Apply'}
              </Button>
            </FormGroup>
          </Paper>
        </DispatchContext.Provider>
      </StateContext.Provider>
    );
  };
}

import React, { useEffect, useReducer } from 'react';
import axios from 'axios';
import set from 'lodash.set';

import Button from '@material-ui/core/Button';
import CircularProgress from '@material-ui/core/CircularProgress';
import Grid from '@material-ui/core/Grid';

import LcdSettings from './LcdSettings';
import LedSettings from './LedSettings';

const reducer = (state, { type, payload }) => {
  switch (type) {
    case 'request':
      return {
        ...state,
        loading: true,
        error: null,
      };
    case 'response':
      return {
        ...state,
        loading: false,
        modified: false,
        data: payload,
        error: null,
      };
    case 'error':
      return {
        ...state,
        loading: false,
        error: payload,
      };
    case 'set':
      return {
        ...state,
        modified: true,
        data: set(state.data, payload.setting, payload.value),
      };
    default:
      return state;
  }
};

const initialState = {
  loading: false,
  modified: false,
  data: null,
  error: null,
};

const apiRequest = (dispatch, data) => {
  dispatch({ type: 'request' });

  // If data is given, assume it's a POST
  const options = data ? { method: 'POST', data } : { method: 'GET' };

  axios('/api', options)
    .then(response => {
      dispatch({ type: 'response', payload: response.data });
    })
    .catch(error => {
      dispatch({ type: 'error', payload: error.response });
    });
};

const Settings = () => {
  const [{ loading, modified, data }, dispatch] = useReducer(
    reducer,
    initialState
  );

  // Load data from the API (on mount only)
  useEffect(() => apiRequest(dispatch), []);

  const setData = (setting, value) =>
    dispatch({ type: 'set', payload: { setting, value } });

  // Data is available, so render settings
  if (data) {
    return (
      <>
        <Grid item>
          <LedSettings data={data.led} setData={setData} />
        </Grid>
        <Grid item>
          <LcdSettings data={data.lcd} setData={setData} />
        </Grid>
        <Grid item>
          <Button
            variant="contained"
            color="primary"
            disabled={loading || !modified}
            onClick={() => apiRequest(dispatch, data)}
          >
            {loading ? <CircularProgress /> : 'Save'}
          </Button>
        </Grid>
      </>
    );
  }

  // No data but we are loading, show a loading indicator
  if (loading) {
    return <CircularProgress />;
  }

  return null;
};

Settings.propTypes = {};

export default Settings;

import PropTypes from 'prop-types';
import React, { useEffect, useReducer } from 'react';
import set from 'lodash.set';

import Button from '@material-ui/core/Button';
import CircularProgress from '@material-ui/core/CircularProgress';

import LcdSettings from './LcdSettings';

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
      console.error(payload);
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
  const options = data
    ? {
        method: 'POST',
        headers: {
          Accept: 'application/json',
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      }
    : {};

  fetch('/api', options)
    .then(response => response.json())
    .then(resData => {
      dispatch({ type: 'response', payload: resData });
    })
    .catch(error => dispatch({ type: 'error', payload: error }));
};

const Settings = () => {
  const [{ loading, modified, data }, dispatch] = useReducer(
    reducer,
    initialState
  );

  // Load data from the API (on mount only)
  useEffect(() => apiRequest(dispatch), []);

  // Data is available, so render settings
  if (data) {
    return (
      <>
        <LcdSettings
          lcd={data.lcd}
          setData={(setting, value) =>
            dispatch({ type: 'set', payload: { setting, value } })
          }
        />

        <Button
          variant="contained"
          color="primary"
          disabled={loading || !modified}
          onClick={() => apiRequest(dispatch, data)}
        >
          {loading ? <CircularProgress /> : 'Save'}
        </Button>
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

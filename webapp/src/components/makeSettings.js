import React, { useEffect, useReducer } from 'react';
import axios from 'axios';
import isEmpty from 'lodash.isempty';
import merge from 'lodash.merge';
import set from 'lodash.set';

import Button from '@material-ui/core/Button';
import CircularProgress from '@material-ui/core/CircularProgress';

const initialState = {
  loading: false,
  error: null,
  apiData: null,
  modifiedData: null,
};

const reducer = (state, { type, payload }) => {
  console.log(type, payload);
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
        error: null,
        apiData: payload,
        modifiedData: {},
      };
    case 'error':
      return {
        ...state,
        loading: false,
        error: payload,
        apiData: null,
        modifiedData: null,
      };
    case 'set':
      return {
        ...state,
        // Update the appropriate field in the data
        modifiedData: set(state.modifiedData, payload.field, payload.value),
      };
    default:
      return state;
  }
};

const apiRequest = (endpoint, dispatch, data) => {
  dispatch({ type: 'request' });

  // If data is given, assume it's a POST
  const options = data ? { method: 'POST', data } : { method: 'GET' };

  axios(`/api/${endpoint}`, options)
    .then(response => {
      dispatch({ type: 'response', payload: response.data });
    })
    .catch(error => {
      dispatch({ type: 'error', payload: error.response });
    });
};

export default (Component, { endpoint }) => props => {
  const [{ loading, apiData, modifiedData }, dispatch] = useReducer(
    reducer,
    initialState
  );

  // Load data from the API (on mount only)
  useEffect(() => apiRequest(endpoint, dispatch), []);

  const setField = (field, value) =>
    dispatch({ type: 'set', payload: { field, value } });

  if (apiData) {
    // Merge the original API data and the modified fields into one object,
    // to be rendered
    const mergedData = merge({}, apiData, modifiedData);

    return (
      <Component data={mergedData} setField={setField} {...props}>
        <Button
          variant="contained"
          color="primary"
          // Disable if loading or no modifications have been made
          disabled={loading || isEmpty(modifiedData)}
          onClick={() => apiRequest(endpoint, dispatch, modifiedData)}
        >
          {loading ? <CircularProgress size={21} /> : 'Apply'}
        </Button>
      </Component>
    );
  }

  // No data but we are loading, show a loading indicator
  if (loading) {
    return <CircularProgress />;
  }

  // TODO - show errors nicely

  // No data and no loading - probably first render
  return null;
};

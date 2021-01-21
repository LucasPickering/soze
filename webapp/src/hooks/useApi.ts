import axios, { AxiosRequestConfig } from 'axios'; // tslint:disable-line:match-default-export-name
import { useCallback, useMemo, useReducer } from 'react';
import { ApiAction, ApiActionType, ApiState, defaultApiState } from 'types/api';

// Makes a reducer for the given data type
const makeApiReducer = <T>(): React.Reducer<ApiState<T>, ApiAction<T>> => (
  state,
  action
) => {
  switch (action.type) {
    case ApiActionType.Request:
      return {
        ...state,
        loading: true,
        data: undefined,
        error: undefined,
      };
    case ApiActionType.Success:
      return {
        ...state,
        loading: false,
        data: action.data,
        error: undefined,
      };
    case ApiActionType.Error:
      return {
        ...state,
        loading: false,
        data: undefined,
        error: action.error,
      };
  }
};

interface ReturnVal<T> {
  state: ApiState<T>;
  request: (config: AxiosRequestConfig) => Promise<T>;
}

/**
 * Hook to get/post data from/to the server for the given resource/status
 */
 function useApi<T>(): ReturnVal<T> {
  // Instantiate the reducer for this type, only on the first call
  const reducer = useMemo(() => makeApiReducer<T>(), []);
  const [state, dispatch] = useReducer(reducer, defaultApiState);

  // Everything here is memoized to prevent unnecessary re-renders and
  // effect triggers

  const request = useCallback(
    (config: AxiosRequestConfig) => {
      dispatch({ type: ApiActionType.Request });
      return axios
        .request(config)
        .then(response => {
          const { data } = response;
          dispatch({
            type: ApiActionType.Success,
            data,
          });
          return data;
        })
        .catch(error => {
          dispatch({
            type: ApiActionType.Error,
            error,
          });
          throw error;
        });
    },
    [dispatch]
  );

  return useMemo(
    () => ({
      state,
      request,
    }),
    [state, request]
  );
}

export default useApi;

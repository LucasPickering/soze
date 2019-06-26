import { useEffect, useMemo, useReducer } from 'react';
import {
  DataModifier,
  defaultResourceState,
  Resource,
  ResourceAction,
  ResourceActionType,
  ResourceState,
  Status,
  Statuses,
} from 'types/resource';
import useApi from './useApi';

// Makes a reducer for the given data type
const makeResourceReducer = <T>(): React.Reducer<
  ResourceState<T>,
  ResourceAction<T>
> => (state, action) => {
  switch (action.type) {
    case ResourceActionType.SetStatus:
      return {
        ...state,
        status: action.status,
      };
    case ResourceActionType.SetData:
      return {
        ...state,
        data: action.value,
        // Whenever we set all data, we should wipe out any modifications
        modifiedData: {},
      };
    case ResourceActionType.ModifyData:
      return {
        ...state,
        // Overwrite any specified keys
        modifiedData: {
          // We want an error if this is called while modifiedData is undef
          ...state.modifiedData!,
          ...action.value,
        },
      };
  }
};

type FetchApiType<T> = Statuses<T>;
type SaveApiType<T> = Partial<T>;

interface ReturnVal<T> {
  state: ResourceState<T>;
  fetchLoading: boolean;
  saveLoading: boolean;
  setStatus: (status: Status) => void;
  modifyData: DataModifier<T>;
  saveData: () => void;
}

/**
 * Hook to get/post data from/to the server for the given resource/status
 */
export default function<T>(resource: Resource): ReturnVal<T> {
  // Instantiate the reducer for this type, only on the first call
  const reducer = useMemo(() => makeResourceReducer<T>(), []);
  const [state, dispatch] = useReducer(reducer, defaultResourceState);

  // Create two API endpoint handlers: One for fetching, one for saving
  const { state: fetchState, request: fetchRequest } = useApi<FetchApiType<T>>(
    `/api/${resource}`
  );
  const { state: saveState, request: saveRequest } = useApi<SaveApiType<T>>(
    `/api/${resource}/${state.status}`
  );

  // Fetch data across all statuses for this resource
  useEffect(() => fetchRequest({ method: 'GET' }), [fetchRequest]);

  // When new fetch or save data is loaded, update our copy of the data
  // If there is no data, don't overwrite existing data
  useEffect(() => {
    if (fetchState.data) {
      dispatch({
        type: ResourceActionType.SetData,
        value: fetchState.data,
      });
    }
  }, [fetchState.data]);
  useEffect(() => {
    const { status, data } = state;
    if (saveState.data) {
      // We shouldn't ever be getting a POST response if we haven't loaded any
      // data yet
      const currentValueForStatus = data![status];
      dispatch({
        type: ResourceActionType.SetData,
        value: {
          // Keep all inactive statuses
          ...data!,
          // The new saveState data will be a Partial<T>, so override any new
          // fields we have and keep everything else
          [status]: {
            ...currentValueForStatus,
            ...saveState.data,
          },
        },
      });
    }
  }, [saveState.data]);

  // Memoize these to prevent unnecessary re-renders
  const setStatus = useMemo(
    () => (status: Status) =>
      dispatch({
        type: ResourceActionType.SetStatus,
        status,
      }),
    [dispatch]
  );
  const modifyData = useMemo(
    () => (value: Partial<T>) =>
      dispatch({
        type: ResourceActionType.ModifyData,
        value,
      }),
    [dispatch]
  );
  const saveData = useMemo(
    () => () => saveRequest({ method: 'POST', data: state.modifiedData }),
    [saveRequest, state.modifiedData]
  );

  return useMemo(
    () => ({
      state,
      fetchLoading: fetchState.loading,
      saveLoading: saveState.loading,
      setStatus,
      modifyData,
      saveData,
    }),
    [
      state,
      fetchState.loading,
      saveState.loading,
      setStatus,
      modifyData,
      saveData,
    ]
  );
}

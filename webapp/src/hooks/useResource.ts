import { clone, isArray, isEqual, mergeWith } from 'lodash-es';
import { useEffect, useMemo, useReducer } from 'react';
import { RecursivePartial } from 'types/core';
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

const objectOnlyMerger = (val: any) => {
  // Don't merge arrays together, just overwrite
  if (isArray(val)) {
    return val;
  }
  return undefined; // Use default behavior
};

// Makes a reducer for the given data type
const makeResourceReducer = <T>(): React.Reducer<
  ResourceState<T>,
  ResourceAction<T>
> => (state: ResourceState<T>, action: ResourceAction<T>) => {
  switch (action.type) {
    case ResourceActionType.SetStatus:
      return {
        ...state,
        status: action.status,
        modifiedData: state.data && state.data[action.status],
      };
    case ResourceActionType.SetData:
      return {
        ...state,
        data: action.value,
        // Whenever we set all data, we should wipe out any modifications
        modifiedData: action.value[state.status],
      };
    case ResourceActionType.ModifyData:
      return {
        ...state,
        // Recursively merge into the existing data
        modifiedData: mergeWith(
          clone(state.modifiedData),
          action.value,
          objectOnlyMerger
        ),
      };
  }
};

interface ReturnVal<T> {
  status: Status;
  modifiedData?: T;
  isModified: boolean;
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
  const { state: fetchState, request: fetchRequest } = useApi<Statuses<T>>(
    `/api/${resource}`
  );
  const { state: saveState, request: saveRequest } = useApi<T>(
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
      dispatch({
        type: ResourceActionType.SetData,
        value: {
          // Keep all inactive statuses. We shouldn't ever be getting a POST
          // response if we haven't loaded any data yet, so this is safe.
          ...data!,
          [status]: saveState.data,
        },
      });
    }
    // This is intentionally missing state as a dependency, we only want to run
    // it when a save response comes in
  }, [saveState.data]);

  // Memoize these to prevent unnecessary re-renders
  const originalDataForStatus = state.data && state.data[state.status];
  const isModified = useMemo(
    () => !isEqual(originalDataForStatus, state.modifiedData),
    [originalDataForStatus, state.modifiedData]
  );
  const setStatus = useMemo(
    () => (status: Status) =>
      dispatch({
        type: ResourceActionType.SetStatus,
        status,
      }),
    [dispatch]
  );
  const modifyData = useMemo(
    () => (value: RecursivePartial<T>) =>
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
      status: state.status,
      isModified,
      modifiedData: state.modifiedData,
      fetchLoading: fetchState.loading,
      saveLoading: saveState.loading,
      setStatus,
      modifyData,
      saveData,
    }),
    [
      state.status,
      isModified,
      state.modifiedData,
      fetchState.loading,
      saveState.loading,
      setStatus,
      modifyData,
      saveData,
    ]
  );
}

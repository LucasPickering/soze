import axios from 'axios';
import { useEffect, useMemo, useReducer } from 'react';
import {
  DataModifier,
  defaultResourceState,
  makeResourceReducer,
  ResourceAction,
  ResourceActionType,
  ResourceState,
} from 'state/resource';
import { Resource, Status } from 'state/types';

interface ReturnVal<T> {
  state: ResourceState<T>;
  setStatus: (status: Status) => void;
  modifyData: DataModifier<T>;
  saveData: () => void;
}

function getUrl(resource: Resource, status?: Status): string {
  return status ? `/api/${resource}/${status}` : `/api/${resource}`;
}

function setStatus<T>(
  dispatch: React.Dispatch<ResourceAction<T>>,
  status: Status
) {
  dispatch({
    type: ResourceActionType.SetStatus,
    status,
  });
}

function modifyData<T>(
  dispatch: React.Dispatch<ResourceAction<T>>,
  modifiedData: Partial<T>
) {
  dispatch({
    type: ResourceActionType.ModifyData,
    value: modifiedData,
  });
}

function saveData<T>(
  dispatch: React.Dispatch<ResourceAction<T>>,
  resource: Resource,
  status: Status,
  data: Partial<T>
) {
  dispatch({ type: ResourceActionType.Post });
  axios
    .post(getUrl(resource, status), data)
    .then(response => {
      dispatch({
        type: ResourceActionType.Success,
        data: response.data,
      });
    })
    .catch(err => {
      dispatch({ type: ResourceActionType.Error, error: err });
    });
}

/**
 * Hook to get/post data from/to the server for the given resource/status
 */
export default function<T>(resource: Resource): ReturnVal<T> {
  // Instantiate the reducer for this type, only on the first call
  const reducer = useMemo(() => makeResourceReducer<T>(), []);
  const [state, dispatch] = useReducer(reducer, defaultResourceState);

  useEffect(() => {
    // Fetch from the API
    axios
      .get(getUrl(resource, state.status))
      .then(response => {
        dispatch({
          type: ResourceActionType.Success,
          data: response.data,
        });
      })
      .catch(err => {
        dispatch({ type: ResourceActionType.Error, error: err });
      });
    dispatch({ type: ResourceActionType.Fetch });
  }, [resource, state.status]);

  return {
    state,
    setStatus: s => setStatus(dispatch, s),
    modifyData: v => modifyData(dispatch, v),
    saveData: () =>
      saveData(dispatch, resource, state.status, state.modifiedData!),
  };
}

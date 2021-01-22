import { cloneDeep, get, isArray, isEqual, mergeWith, noop } from 'lodash-es';
import { useEffect, useReducer } from 'react';
import { RecursivePartial } from 'types/core';
import {
  defaultResourceState,
  Resource,
  ResourceAction,
  ResourceActionType,
  ResourceState,
  Status,
  Statuses,
} from 'types/resource';
import useApi from './useApi';

const mergeObjects = (obj: any, ...other: any): any => {
  return mergeWith(obj, ...other, (_: any, srcVal: any) => {
    // Don't merge arrays together, just overwrite
    return isArray(srcVal) ? srcVal : undefined;
  });
};

// Makes a reducer for the given data type
const reducer = <T>(
  state: ResourceState<T>,
  action: ResourceAction<T>
): ResourceState<T> => {
  switch (action.type) {
    case ResourceActionType.SetStatus:
      return {
        ...state,
        status: action.status,
      };
    case ResourceActionType.FetchLoad:
      return {
        ...state,
        data: action.data,
        // Whenever we set all data, we should wipe out any modifications
        modifiedData: cloneDeep(action.data),
      };
    case ResourceActionType.PostLoad:
      return {
        ...state,
        data: { ...state.data, [action.status]: action.data },
      };
    case ResourceActionType.ModifyData:
      return {
        ...state,
        // Recursively merge into the existing data
        modifiedData: mergeObjects(state.modifiedData, {
          [action.status]: action.data,
        }),
      };
  }
};

interface ReturnVal<T> {
  status: Status;
  localData?: T;
  isModified: boolean;
  fetchLoading: boolean;
  postLoading: boolean;
  setStatus: (status: Status) => void;
  modifyData: (value: RecursivePartial<T>) => void;
  saveData: () => void;
}

/**
 * Hook to get/post data from/to the server for the given resource/status
 */
function useResource<T>(resource: Resource): ReturnVal<T> {
  const [state, dispatch] = useReducer<
    React.Reducer<ResourceState<T>, ResourceAction<T>>
  >(reducer, defaultResourceState);

  // Create two API endpoint handlers: One for fetching, one for saving
  const {
    state: { loading: fetchLoading },
    request: fetchRequest,
  } = useApi<Statuses<T>>();
  const {
    state: { loading: putLoading },
    request: putRequest,
  } = useApi<T>();

  // Fetch data across all statuses for this resource
  useEffect(() => {
    fetchRequest({ url: `/api/${resource}`, method: 'GET' })
      .then(fetchData => {
        dispatch({
          type: ResourceActionType.FetchLoad,
          data: fetchData,
        });
      })
      .catch(noop);
  }, [fetchRequest, resource]);

  const { status, data, modifiedData } = state;
  const modifiedForStatus = modifiedData && modifiedData[status];

  return {
    status,
    isModified: !isEqual(data, modifiedData),
    localData: get(mergeObjects(data, modifiedData), status),
    fetchLoading,
    postLoading: putLoading,
    setStatus: (s: Status) => {
      dispatch({
        type: ResourceActionType.SetStatus,
        status: s,
      });
    },
    modifyData: (newData: RecursivePartial<T>) => {
      dispatch({
        type: ResourceActionType.ModifyData,
        status,
        data: newData,
      });
    },
    saveData: () =>
      putRequest({
        url: `/api/${resource}/${status}`,
        method: 'PUT',
        data: modifiedForStatus,
      })
        .then(postData => {
          dispatch({
            type: ResourceActionType.PostLoad,
            status,
            data: postData,
          });
        })
        .catch(noop),
  };
}

export default useResource;

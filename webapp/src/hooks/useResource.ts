import axios from 'axios'; // tslint:disable-line:match-default-export-name
import { useEffect, useMemo, useReducer } from 'react';
import {
  DataModifier,
  defaultResourceState,
  ResourceAction,
  ResourceActionType,
  ResourceState,
} from 'state/types';
import { Resource, Status } from 'state/types';

interface ReturnVal<T> {
  state: ResourceState<T>;
  setStatus: (status: Status) => void;
  modifyData: DataModifier<T>;
  saveData: () => void;
}

// Makes a reducer for the given data type
const makeResourceReducer = <T>(): React.Reducer<
  ResourceState<T>,
  ResourceAction<T>
> => (state, action) => {
  switch (action.type) {
    case ResourceActionType.Fetch:
      return {
        ...state,
        data: undefined,
        fetch: {
          loading: true,
          error: undefined,
        },
      };
    case ResourceActionType.FetchSuccess:
      return {
        ...state,
        data: action.data,
        modifiedData: {},
        fetch: {
          loading: false,
          error: undefined,
        },
      };
    case ResourceActionType.FetchError:
      return {
        ...state,
        fetch: {
          loading: false,
          error: action.error,
        },
      };
    case ResourceActionType.Save:
      return {
        ...state,
        save: {
          loading: true,
          error: undefined,
        },
      };
    case ResourceActionType.SaveSuccess:
      return {
        ...state,
        data: {
          ...state.data,
          [state.status]: action.data,
        },
        modifiedData: {},
        save: {
          loading: false,
          error: undefined,
        },
      };
    case ResourceActionType.SaveError:
      return {
        ...state,
        save: {
          loading: false,
          error: action.error,
        },
      };
    case ResourceActionType.SetStatus:
      return {
        ...state,
        status: action.status,
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
    default:
      return state;
  }
};

function getUrl(resource: Resource, status?: Status): string {
  return status ? `/api/${resource}/${status}` : `/api/${resource}`;
}

function saveData<T>(
  dispatch: React.Dispatch<ResourceAction<T>>,
  resource: Resource,
  status: Status,
  data: Partial<T>
) {
  dispatch({ type: ResourceActionType.Save });
  axios
    .post(getUrl(resource, status), data)
    .then(response => {
      dispatch({
        type: ResourceActionType.SaveSuccess,
        data: response.data,
      });
    })
    .catch(err => {
      dispatch({ type: ResourceActionType.SaveError, error: err });
    });
}

/**
 * Hook to get/post data from/to the server for the given resource/status
 */
export default function<T>(resource: Resource): ReturnVal<T> {
  // Instantiate the reducer for this type, only on the first call
  const reducer = useMemo(() => makeResourceReducer<T>(), []);
  const [state, dispatch] = useReducer(reducer, defaultResourceState);

  // Fetch data across all statuses for this resource
  useEffect(() => {
    axios
      .get(`/api/${resource}`)
      .then(response => {
        dispatch({
          type: ResourceActionType.FetchSuccess,
          data: response.data,
        });
      })
      .catch(err => {
        dispatch({ type: ResourceActionType.SaveError, error: err });
      });
    dispatch({ type: ResourceActionType.Fetch });
  }, [resource]);

  const modifyData = useMemo(
    () => (value: Partial<T>) =>
      dispatch({
        type: ResourceActionType.ModifyData,
        value,
      }),
    [dispatch]
  );

  return useMemo(
    () => ({
      state,
      setStatus: status =>
        dispatch({
          type: ResourceActionType.SetStatus,
          status,
        }),
      modifyData,
      saveData: () =>
        saveData(dispatch, resource, state.status, state.modifiedData!),
    }),
    [resource, state, dispatch, modifyData]
  );
}

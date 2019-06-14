import axios from 'axios';
import { useEffect, useReducer } from 'react';
import {
  DataModifier,
  defaultResourceState,
  makeResourceReducer,
  ResourceActionType,
  ResourceState,
} from 'state/resource';
import { Status } from 'state/types';

interface ReturnVal<T> {
  state: ResourceState<T>;
  modifyData: DataModifier<T>;
  saveData: () => void;
}

/**
 * Creates a useResource hook for the given type
 */
export default function<T>(resource: string) {
  const reducer = makeResourceReducer<T>();
  return (status: Status): ReturnVal<T> => {
    const url = `/api/${resource}/${status}`;
    const [state, dispatch] = useReducer(reducer, defaultResourceState);

    useEffect(() => {
      // Fetch from the API
      axios
        .get(url)
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
    }, [status, url]);

    return {
      state,
      modifyData: modifiedData =>
        dispatch({
          type: ResourceActionType.Modify,
          value: modifiedData,
        }),
      saveData: () => {
        // POST to the API
        dispatch({ type: ResourceActionType.Post });
        axios
          .post(url, state.modifiedData)
          .then(response => {
            dispatch({
              type: ResourceActionType.Success,
              data: response.data,
            });
          })
          .catch(err => {
            dispatch({ type: ResourceActionType.Error, error: err });
          });
      },
    };
  };
}

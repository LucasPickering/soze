import axios from 'axios';
import React from 'react';
import { Status } from './types';

export interface ResourceState<T> {
  loading: boolean;
  status: Status;
  data?: T;
  modifiedData?: Partial<T>;
  error?: string; // TODO
}

export const defaultResourceState: ResourceState<any> = {
  loading: false,
  status: Status.Normal,
  data: undefined,
  modifiedData: undefined,
  error: undefined,
};

export enum ResourceActionType {
  Fetch,
  Post,
  Success,
  Error,
  Modify,
}

export type ResourceAction<T> =
  | { type: ResourceActionType.Fetch }
  | { type: ResourceActionType.Post }
  | { type: ResourceActionType.Success; data: T }
  | { type: ResourceActionType.Error; error: string }
  | { type: ResourceActionType.Modify; value: Partial<T> };

// Makes a reducer for the given data type
export const makeResourceReducer = <T>(): React.Reducer<
  ResourceState<T>,
  ResourceAction<T>
> => (state, action) => {
  switch (action.type) {
    case ResourceActionType.Fetch:
      return {
        ...state,
        loading: true,
        data: undefined,
        error: undefined,
      };
    case ResourceActionType.Post:
      return {
        ...state,
        loading: true,
      };
    case ResourceActionType.Success:
      return {
        ...state,
        loading: false,
        data: action.data,
        modifiedData: {},
      };
    case ResourceActionType.Error:
      return {
        ...state,
        loading: false,
        error: action.error,
      };
    case ResourceActionType.Modify:
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

export type DataModifier<T> = (value: Partial<T>) => void;

export function apiRequest<T>(
  resource: string,
  status: Status,
  data?: Partial<T>
) {
  // If data is given, assume it's a POST
  const options = data ? { method: 'POST', data } : { method: 'GET' };

  return axios.post(`/api/${resource}/${status}`, options);
}

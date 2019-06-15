import React from 'react';
import { Status } from './types';

export interface ResourceState<T> {
  status: Status;
  loading: boolean;
  data?: T;
  modifiedData?: Partial<T>;
  error?: string; // TODO
}

export const defaultResourceState: ResourceState<any> = {
  status: Status.Normal,
  loading: false,
  data: undefined,
  modifiedData: undefined,
  error: undefined,
};

export enum ResourceActionType {
  Fetch,
  Post,
  Success,
  Error,
  SetStatus,
  ModifyData,
}

export type ResourceAction<T> =
  | { type: ResourceActionType.Fetch }
  | { type: ResourceActionType.Post }
  | { type: ResourceActionType.Success; data: T }
  | { type: ResourceActionType.Error; error: string }
  | { type: ResourceActionType.SetStatus; status: Status }
  | { type: ResourceActionType.ModifyData; value: Partial<T> };

export type DataModifier<T> = (value: Partial<T>) => void;

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

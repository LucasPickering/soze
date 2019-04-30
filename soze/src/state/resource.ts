import axios from 'axios';
import { set } from 'lodash-es';
import React from 'react';

export interface ResourceState<T> {
  loading: boolean;
  data?: T;
  modifiedData?: Partial<T>;
  error?: string; // TODO
}

export const defaultResourceState: ResourceState<any> = {
  loading: false,
  data: undefined,
  error: undefined,
};

export enum ResourceActionType {
  Request,
  Success,
  Error,
  Modify,
}

export type ResourceAction<T> =
  | { type: ResourceActionType.Request }
  | { type: ResourceActionType.Success; data: T }
  | { type: ResourceActionType.Error; error: string }
  | { type: ResourceActionType.Modify; field: string; value: Partial<T> };

// Makes a reducer for the given data type
const makeResourceReducer = <T>(): React.Reducer<
  ResourceState<T>,
  ResourceAction<T>
> => (state, action) => {
  switch (action.type) {
    case ResourceActionType.Request:
      return {
        ...state,
        loading: true,
        data: undefined,
        error: undefined,
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
        // We want an error if this is called while modifiedData is undef
        modifiedData: set(state.modifiedData!, action.field, action.value),
      };
  }
};

// Params => URL
export type RequestBuilder<Params> = (params: Params) => string;

export type DataTransformer<InputData, OutputData> = (
  data: InputData
) => OutputData;

const makeFetcher = <Data>(resource: string) => (
  dispatch: React.Dispatch<ResourceAction<Data>>,
  status: string
) => {
  dispatch({ type: ResourceActionType.Request });
  axios
    .get(`/api/${resource}/${status}`)
    .then(response => {
      dispatch({
        type: ResourceActionType.Success,
        data: response.data,
      });
    })
    .catch(err => {
      dispatch({ type: ResourceActionType.Error, error: err });
    });
};

export interface ResourceKit<T> {
  reducer: React.Reducer<ResourceState<T>, ResourceAction<T>>;
  fetcher: (
    dispatch: React.Dispatch<ResourceAction<T>>,
    status: string
  ) => void;
  contexts: [
    React.Context<ResourceState<T>>,
    React.Context<React.Dispatch<ResourceAction<T>>>
  ];
}

export const makeResourceKit = <Data>(resource: string): ResourceKit<Data> => ({
  reducer: makeResourceReducer<Data>(),
  fetcher: makeFetcher<Data>(resource),
  contexts: [
    // This default values should never be used, just there to appease TS
    React.createContext<ResourceState<Data>>({} as ResourceState<Data>),
    React.createContext<React.Dispatch<ResourceAction<Data>>>(
      {} as React.Dispatch<ResourceAction<Data>>
    ),
  ],
});

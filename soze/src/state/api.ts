import axios from 'axios';
import React from 'react';
import makeReducerContexts from './makeReducerContexts';

export interface ApiState<T> {
  loading: boolean;
  data?: T;
  error?: string; // TODO
}

export const defaultApiState: ApiState<any> = {
  loading: false,
  data: undefined,
  error: undefined,
};

export enum ApiActionType {
  Request,
  Success,
  Error,
}

export type ApiAction<T> =
  | { type: ApiActionType.Request }
  | { type: ApiActionType.Success; data: T }
  | { type: ApiActionType.Error; error: string };

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
      };
    case ApiActionType.Error:
      return {
        ...state,
        loading: false,
        error: action.error,
      };
  }
};

// Params => URL
export type RequestBuilder<Params> = (params: Params) => string;

export type DataTransformer<InputData, OutputData> = (
  data: InputData
) => OutputData;

const makeFetcher = <Params, Data>(requestBuilder: RequestBuilder<Params>) => (
  dispatch: React.Dispatch<ApiAction<Data>>,
  params: Params
) => {
  dispatch({ type: ApiActionType.Request });
  axios
    .get(requestBuilder(params))
    .then(response => {
      dispatch({
        type: ApiActionType.Success,
        data: response.data,
      });
    })
    .catch(err => {
      dispatch({ type: ApiActionType.Error, error: err });
    });
};

export const makeApiKit = <Params, Data>(
  requestBuilder: RequestBuilder<Params>
) => ({
  reducer: makeApiReducer<Data>(),
  fetcher: makeFetcher<Params, Data>(requestBuilder),
  contexts: makeReducerContexts<ApiState<Data>, ApiAction<Data>>(),
});

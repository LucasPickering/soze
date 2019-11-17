import { RecursivePartial } from './core';

export enum Resource {
  LED = 'led',
  LCD = 'lcd',
}

export enum Status {
  Normal = 'normal',
  Sleep = 'sleep',
}

export interface Statuses<T> {
  [status: string]: T;
}

export interface ResourceState<T> {
  status: Status;
  data?: Statuses<T>;
  modifiedData?: Statuses<RecursivePartial<T>>;
}

export const defaultResourceState: ResourceState<any> = {
  status: Status.Normal,
};

export enum ResourceActionType {
  SetStatus,
  FetchLoad, // When a GET response comes in, for all statuses
  PostLoad, // When a POST response comes in, for just one status
  ModifyData,
}

export type ResourceAction<T> =
  | { type: ResourceActionType.SetStatus; status: Status }
  | { type: ResourceActionType.FetchLoad; data: Statuses<T> }
  | { type: ResourceActionType.PostLoad; status: Status; data: T }
  | {
      type: ResourceActionType.ModifyData;
      status: Status;
      data: RecursivePartial<T>;
    };

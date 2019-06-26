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
  modifiedData?: T;
}

export const defaultResourceState: ResourceState<any> = {
  status: Status.Normal,
  modifiedData: undefined,
};

export enum ResourceActionType {
  SetStatus,
  SetData,
  ModifyData,
}

export type ResourceAction<T> =
  | { type: ResourceActionType.SetStatus; status: Status }
  | { type: ResourceActionType.SetData; value: Statuses<T> }
  | { type: ResourceActionType.ModifyData; value: RecursivePartial<T> };

export type DataModifier<T> = (value: RecursivePartial<T>) => void;

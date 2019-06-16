// An HTML color code, like #ff0000
export type Color = string;

export enum Resource {
  LED = 'led',
  LCD = 'lcd',
}

export enum Status {
  Normal = 'normal',
  Sleep = 'sleep',
}

export enum LedMode {
  Off = 'off',
  Static = 'static',
  Fade = 'fade',
}

export interface LedSettings {
  mode: LedMode;
  static: {
    color: Color;
  };
  fade: {
    colors: Color[];
    saved: {
      name: string;
      colors: Color[];
    };
    fade_time: number;
  };
}

export enum LcdMode {
  Off = 'off',
  Clock = 'clock',
}

export interface LcdSettings {
  mode: LcdMode;
  color: Color;
}

export interface Statuses<T> {
  [status: string]: T;
}

export interface ResourceState<T> {
  status: Status;
  loading: boolean;
  data?: Statuses<T>;
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
  FetchSuccess,
  Post,
  PostSuccess,
  Error,
  SetStatus,
  ModifyData,
}

export type ResourceAction<T> =
  | { type: ResourceActionType.Fetch }
  | { type: ResourceActionType.FetchSuccess; data: Statuses<T> }
  | { type: ResourceActionType.Post }
  | { type: ResourceActionType.PostSuccess; data: T }
  | { type: ResourceActionType.Error; error: string }
  | { type: ResourceActionType.SetStatus; status: Status }
  | { type: ResourceActionType.ModifyData; value: Partial<T> };

export type DataModifier<T> = (value: Partial<T>) => void;

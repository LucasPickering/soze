// An HTML color code, like #ff0000
export type Color = string;

export type Error = string; // TODO

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
  data?: Statuses<T>;
  modifiedData?: Partial<T>;
  fetch: {
    loading: boolean;
    error?: Error;
  };
  save: {
    loading: boolean;
    error?: Error;
  };
}

export const defaultResourceState: ResourceState<any> = {
  status: Status.Normal,
  data: undefined,
  modifiedData: undefined,
  fetch: {
    loading: false,
    error: undefined,
  },
  save: {
    loading: false,
    error: undefined,
  },
};

export enum ResourceActionType {
  Fetch,
  FetchSuccess,
  FetchError,
  Save,
  SaveSuccess,
  SaveError,
  SetStatus,
  ModifyData,
}

export type ResourceAction<T> =
  | { type: ResourceActionType.Fetch }
  | { type: ResourceActionType.FetchSuccess; data: Statuses<T> }
  | { type: ResourceActionType.FetchError; error: Error }
  | { type: ResourceActionType.SaveError; error: Error }
  | { type: ResourceActionType.Save }
  | { type: ResourceActionType.SaveSuccess; data: T }
  | { type: ResourceActionType.SaveError; error: Error }
  | { type: ResourceActionType.SetStatus; status: Status }
  | { type: ResourceActionType.ModifyData; value: Partial<T> };

export type DataModifier<T> = (value: Partial<T>) => void;

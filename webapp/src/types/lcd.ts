import { Color } from './core';

export enum LcdMode {
  Off = 'off',
  Clock = 'clock',
}

export interface LcdSettings {
  mode: LcdMode;
  color: Color;
}

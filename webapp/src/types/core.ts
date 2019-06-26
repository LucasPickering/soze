// An HTML color code, like #ff0000
export type Color = string;

export type Error = string; // TODO

// https://stackoverflow.com/questions/47914536/use-partial-in-nested-property-with-typescript
export type RecursivePartial<T> = {
  [P in keyof T]?: RecursivePartial<T[P]>;
};

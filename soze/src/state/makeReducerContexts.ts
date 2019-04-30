import React from 'react';

export default function<State, Action>(): [
  React.Context<State>,
  React.Context<React.Dispatch<Action>>
] {
  return [
    // This default values should never be used, just there to appease TS
    React.createContext<State>({} as State),
    React.createContext<React.Dispatch<Action>>({} as React.Dispatch<Action>),
  ];
}

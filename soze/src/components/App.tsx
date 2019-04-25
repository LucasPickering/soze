import { createMuiTheme, Theme } from '@material-ui/core';
import CssBaseline from '@material-ui/core/CssBaseline';
import { makeStyles, ThemeProvider } from '@material-ui/styles';
import React from 'react';
import './App.css';

const theme = createMuiTheme({
  palette: {
    type: 'light',
  },
  typography: {
    useNextVariants: true,
  },
});

const useLocalStyles = makeStyles(({ spacing }: Theme) => ({
  root: {},
}));

const App: React.FC = () => {
  const localClasses = useLocalStyles();
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <div className={localClasses.root} />
    </ThemeProvider>
  );
};

export default App;

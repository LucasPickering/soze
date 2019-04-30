import { createMuiTheme, Grid, Theme, Typography } from '@material-ui/core';
import CssBaseline from '@material-ui/core/CssBaseline';
import { makeStyles, ThemeProvider } from '@material-ui/styles';
import React from 'react';
import LcdControls from './LcdControls';

const theme = createMuiTheme({
  palette: {
    type: 'dark',
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
      <Grid container direction="column" alignItems="center">
        <Typography variant="h2">Söze</Typography>
        <Grid item container direction="column" alignItems="center">
          {/* <Grid item>
            <LedSettings />
          </Grid> */}
          <Grid item>
            <LcdControls />
          </Grid>
        </Grid>
      </Grid>
    </ThemeProvider>
  );
};

export default App;

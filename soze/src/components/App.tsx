import { createMuiTheme, Grid, Typography } from '@material-ui/core';
import CssBaseline from '@material-ui/core/CssBaseline';
import { ThemeProvider } from '@material-ui/styles';
import React from 'react';
import LcdContainer from './LcdContainer';
import LedContainer from './LedContainer';

const theme = createMuiTheme({
  palette: {
    type: 'dark',
  },
});

const App: React.FC = () => (
  <ThemeProvider theme={theme}>
    <CssBaseline />
    <Grid container direction="column" alignItems="center">
      <Typography variant="h2">Söze</Typography>
      <Grid item container direction="column" alignItems="center">
        <Grid item>
          <LedContainer />
        </Grid>
        <Grid item>
          <LcdContainer />
        </Grid>
      </Grid>
    </Grid>
  </ThemeProvider>
);

export default App;

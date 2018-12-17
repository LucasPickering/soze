import PropTypes from 'prop-types';
import React from 'react';

import {
  MuiThemeProvider,
  createMuiTheme,
  withStyles,
} from '@material-ui/core/styles';
import CssBaseline from '@material-ui/core/CssBaseline';
import Grid from '@material-ui/core/Grid';
import Typography from '@material-ui/core/Typography';

import Settings from './Settings';

const theme = createMuiTheme({
  palette: {
    type: 'light',
  },
  typography: {
    useNextVariants: true,
  },
});

const styles = ({ spacing }) => ({
  root: {
    flexGrow: 1,
    padding: spacing.unit,
  },
});

const App = ({ classes }) => (
  <MuiThemeProvider theme={theme}>
    <div className={classes.root}>
      <CssBaseline />
      <Grid
        container
        direction="column"
        alignItems="center"
        spacing={theme.spacing.unit}
      >
        <Typography variant="h2">Söze</Typography>
        <Settings />
      </Grid>
    </div>
  </MuiThemeProvider>
);

App.propTypes = {
  classes: PropTypes.shape().isRequired,
};

export default withStyles(styles)(App);

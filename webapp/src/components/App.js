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
import styles from '../styles';

const theme = createMuiTheme({
  palette: {
    type: 'dark',
  },
  typography: {
    useNextVariants: true,
  },
  overrides: {
    MuiFormControl: {
      root: {
        // Keep controls from growing to their parent
        display: 'inline-block',
      },
    },
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
        <Grid
          item
          container
          direction="column"
          alignItems="center"
          spacing={theme.spacing.unit}
        >
          <Settings />
        </Grid>
      </Grid>
    </div>
  </MuiThemeProvider>
);

App.propTypes = {
  classes: PropTypes.shape().isRequired,
};

export default withStyles(styles)(App);

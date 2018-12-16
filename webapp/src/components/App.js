import PropTypes from 'prop-types';
import React, { useEffect, useState } from 'react';

import {
  MuiThemeProvider,
  createMuiTheme,
  withStyles,
} from '@material-ui/core/styles';
import Button from '@material-ui/core/Button';
import CircularProgress from '@material-ui/core/CircularProgress';
import CssBaseline from '@material-ui/core/CssBaseline';
import Grid from '@material-ui/core/Grid';
import Typography from '@material-ui/core/Typography';

import LcdSettings from './LcdSettings';

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
  paper: {
    padding: spacing.unit * 2,
    display: 'flex',
    flexDirection: 'column',
  },
});

const fetchData = ({ setLoading, setData, setModified, data }) => {
  setLoading(true);
  fetch('/api', { method: data ? 'post' : 'get' })
    .then(response => response.json())
    .then(responseData => {
      setLoading(false);
      setModified(false);
      setData(responseData);
    });
};

const App = ({ classes }) => {
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState(null);
  const [modified, setModified] = useState(false);

  // Load data from the API (on mount only)
  useEffect(() => {
    setLoading(true);
    fetch('/api')
      .then(response => response.json())
      .then(responseData => {
        setLoading(false);
        setModified(false);
        setData(responseData);
      });
  }, []);

  if (!data) {
    return null;
  }

  return (
    <MuiThemeProvider theme={theme}>
      <div className={classes.root}>
        <CssBaseline />
        <Grid
          container
          direction="column"
          alignItems="center"
          spacing={theme.spacing.unit}
        >
          <Grid item>
            <Typography variant="h2">Söze</Typography>
          </Grid>
          {loading ? (
            <Grid item>
              <CircularProgress className={classes.progress} />
            </Grid>
          ) : (
            <>
              <Grid item>
                <LcdSettings classes={classes} lcd={data.lcd} />
              </Grid>

              <Grid item>
                <Button
                  className={classes.button}
                  variant="contained"
                  color="primary"
                  disabled={!modified}
                >
                  Save
                </Button>
              </Grid>
            </>
          )}
        </Grid>
      </div>
    </MuiThemeProvider>
  );
};

App.propTypes = {
  classes: PropTypes.object.isRequired,
};

export default withStyles(styles)(App);

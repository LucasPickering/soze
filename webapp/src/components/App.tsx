import {
  Container,
  createMuiTheme,
  Grid,
  makeStyles,
  Typography,
} from '@material-ui/core';
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

const useLocalStyles = makeStyles(({ breakpoints, spacing }) => ({
  pageContainer: {
    display: 'flex',
    flexDirection: 'column',
    flex: 1,
    alignItems: 'center',

    [breakpoints.only('xs')]: {
      padding: spacing(2),
    },
    [breakpoints.up('sm')]: {
      padding: spacing(4),
    },
  },
}));

const App: React.FC = () => {
  const localClasses = useLocalStyles();
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Container className={localClasses.pageContainer}>
        <Typography variant="h2">Söze</Typography>
        <Grid container justify="center" spacing={2}>
          <Grid item xs={12} sm={6} md={4}>
            <LedContainer />
          </Grid>
          <Grid item xs={12} sm={6} md={4}>
            <LcdContainer />
          </Grid>
        </Grid>
      </Container>
    </ThemeProvider>
  );
};

export default App;

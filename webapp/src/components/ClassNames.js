import { withStyles } from '@material-ui/core/styles';
import Button from '@material-ui/core/Button';
import PropTypes from 'prop-types';
import React from 'react';
import classNames from 'classnames';

// We can inject some CSS into the DOM.
const styles = {
  paper: {
    padding: 12,
    width: 400,
  },
};

function ClassNames(props) {
  const { classes, children, className, ...other } = props;

  return (
    <Button className={classNames(classes.root, className)} {...other}>
      {children || 'class names'}
    </Button>
  );
}

ClassNames.propTypes = {
  className: PropTypes.string,
  classes: PropTypes.shape().isRequired,
  children: PropTypes.node,
};

ClassNames.defaultProps = {
  className: null,
  children: null,
};

export default withStyles(styles)(ClassNames);

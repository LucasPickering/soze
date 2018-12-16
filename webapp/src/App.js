import React, { useEffect, useState } from 'react';

import SozeContext from './Context';
import classes from './App.module.scss';

const App = () => {
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState(null);

  // Load data from the API (on mount only)
  useEffect(() => {
    setLoading(true);
    fetch('/api').then(response => {
      setLoading(false);
      setData(response.json());
    });
  }, []);

  return (
    <div className={classes.app}>
      <SozeContext.Provider value={data}>
        {loading ? <p>Loading...</p> : <div />}
      </SozeContext.Provider>
    </div>
  );
};

export default App;

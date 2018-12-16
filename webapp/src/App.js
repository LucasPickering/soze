import React, { useEffect, useState } from 'react';

import SozeContext from './Context';
import classes from './App.module.scss';

const App = () => {
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState(null);

  // Load data from the API (on mount only)
  useEffect(() => {
    setLoading(true);
    fetch('tyranitar:5000').then(response => {
      setLoading(false);
      setData(response.json());
    });
    // setTimeout(() => {
    //   setLoading(false);
    //   setData({
    //     lcd: { color: '0x000000', link_to_led: false, mode: 'off' },
    //     led: {
    //       fade: { colors: [], fade_time: 5.0, saved: {} },
    //       mode: 'off',
    //       static: { color: '0x000000' },
    //     },
    //   });
    // }, 3000);
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

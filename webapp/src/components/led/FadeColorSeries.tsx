import { FormControl, Typography } from '@material-ui/core';
import ColorSeries from 'components/color/ColorSeries';
import React from 'react';
import { Color } from 'types/core';
import { LedSettings } from 'types/led';
import { DataModifier } from 'types/resource';

interface Props {
  colors: Color[];
  modifyData: DataModifier<LedSettings>;
}

const FadeColorSeries: React.FC<Props> = React.memo(
  ({ colors, modifyData }) => (
    <FormControl>
      <Typography>Color Series</Typography>
      <ColorSeries
        colors={colors}
        setColors={newColors => {
          modifyData({
            fade: { colors: newColors },
          });
        }}
      />
    </FormControl>
  )
);

export default FadeColorSeries;

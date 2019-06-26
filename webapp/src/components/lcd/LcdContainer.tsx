import ResourceControlsContainer from 'components/ResourceControlsContainer';
import useResource from 'hooks/useResource';
import React from 'react';
import { LcdSettings } from 'types/lcd';
import { Resource } from 'types/resource';
import LcdControls from './LcdControls';

interface Props {}

const LcdContainer: React.FC<Props> = () => {
  const { modifiedData: currentData, modifyData, ...rest } = useResource<
    LcdSettings
  >(Resource.LCD);

  return (
    <ResourceControlsContainer title="LCD" {...rest}>
      {currentData && (
        <LcdControls settings={currentData} modifyData={modifyData} />
      )}
    </ResourceControlsContainer>
  );
};

export default LcdContainer;

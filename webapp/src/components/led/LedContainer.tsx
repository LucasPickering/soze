import useResource from 'hooks/useResource';
import React from 'react';
import { LedSettings } from 'types/led';
import { Resource } from 'types/resource';
import ResourceControlsContainer from '../ResourceControlsContainer';
import LedControls from './LedControls';

interface Props {}

const LedContainer: React.FC<Props> = () => {
  const { modifiedData: currentData, modifyData, ...rest } = useResource<
    LedSettings
  >(Resource.LED);

  return (
    <ResourceControlsContainer title="LED" {...rest}>
      {currentData && (
        <LedControls settings={currentData} modifyData={modifyData} />
      )}
    </ResourceControlsContainer>
  );
};

export default LedContainer;

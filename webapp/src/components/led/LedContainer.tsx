import useResource from 'hooks/useResource';
import React from 'react';
import { LedSettings } from 'types/led';
import { Resource } from 'types/resource';
import ResourceControlsContainer from '../ResourceControlsContainer';
import LedControls from './LedControls';

interface Props {}

const LedContainer: React.FC<Props> = () => {
  const resource = useResource<LedSettings>(Resource.LED);
  const {
    state: { status, data, modifiedData },
    modifyData,
  } = resource;

  return (
    <ResourceControlsContainer title="LED" {...resource}>
      {data && (
        <LedControls
          settings={{
            ...data[status],
            ...modifiedData,
          }}
          modifyData={modifyData}
        />
      )}
    </ResourceControlsContainer>
  );
};

export default LedContainer;

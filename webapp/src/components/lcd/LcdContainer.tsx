import ResourceControlsContainer from 'components/ResourceControlsContainer';
import useResource from 'hooks/useResource';
import React from 'react';
import { LcdSettings } from 'types/lcd';
import { Resource } from 'types/resource';
import LcdControls from './LcdControls';

interface Props {}

const LcdContainer: React.FC<Props> = () => {
  const resource = useResource<LcdSettings>(Resource.LCD);
  const {
    state: { status, data, modifiedData },
    modifyData,
  } = resource;

  return (
    <ResourceControlsContainer title="LCD" {...resource}>
      {data && (
        <LcdControls
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

export default LcdContainer;

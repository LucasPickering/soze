import useResource from 'hooks/useResource';
import React from 'react';
import { LedSettings, Resource } from 'state/types';
import LedControls from './LedControls';
import ResourceControlsContainer from './ResourceControlsContainer';

interface Props {}

const LedContainer: React.FC<Props> = () => {
  const { state, setStatus, modifyData, saveData } = useResource<LedSettings>(
    Resource.LED
  );
  const { status, data, modifiedData } = state;

  return (
    <ResourceControlsContainer
      title="LED"
      state={state}
      setStatus={setStatus}
      saveData={saveData}
    >
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

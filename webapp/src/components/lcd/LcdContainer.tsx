import ResourceControlsContainer from 'components/ResourceControlsContainer';
import useResource from 'hooks/useResource';
import React from 'react';
import { LcdSettings, Resource } from 'state/types';
import LcdControls from './LcdControls';

interface Props {}

const LcdContainer: React.FC<Props> = () => {
  const { state, setStatus, modifyData, saveData } = useResource<LcdSettings>(
    Resource.LCD
  );
  const { status, data, modifiedData } = state;

  return (
    <ResourceControlsContainer
      title="LCD"
      state={state}
      setStatus={setStatus}
      saveData={saveData}
    >
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

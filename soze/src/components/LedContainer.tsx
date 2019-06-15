import useResource from 'hooks/useResource';
import { isEmpty } from 'lodash-es';
import React from 'react';
import { LedSettings, Resource } from 'state/types';
import LedControls from './LedControls';
import ResourceControlsContainer from './ResourceControlsContainer';

interface Props {}

const LedContainer: React.FC<Props> = () => {
  const {
    state: { status, loading, data, modifiedData },
    setStatus,
    modifyData,
    saveData,
  } = useResource<LedSettings>(Resource.LED);

  return (
    <ResourceControlsContainer
      title="LED"
      status={status}
      loading={loading}
      modified={!isEmpty(modifiedData)}
      setStatus={setStatus}
      saveData={saveData}
    >
      {data && (
        <LedControls
          settings={{
            ...data,
            ...modifiedData,
          }}
          modifyData={modifyData}
        />
      )}
    </ResourceControlsContainer>
  );
};

export default LedContainer;

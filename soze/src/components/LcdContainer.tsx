import useResource from 'hooks/useResource';
import { isEmpty } from 'lodash-es';
import React from 'react';
import { LcdSettings } from 'state/types';
import LcdControls from './LcdControls';
import ResourceControlsContainer from './ResourceControlsContainer';

interface Props {}

const LcdContainer: React.FC<Props> = () => {
  const {
    state: { status, loading, data, modifiedData },
    setStatus,
    modifyData,
    saveData,
  } = useResource<LcdSettings>('lcd');

  return (
    <ResourceControlsContainer
      title="LCD"
      status={status}
      loading={loading}
      modified={!isEmpty(modifiedData)}
      setStatus={setStatus}
      saveData={saveData}
    >
      {data ? (
        <LcdControls
          settings={{
            ...data,
            ...modifiedData,
          }}
          modifyData={modifyData}
        />
      ) : null}
    </ResourceControlsContainer>
  );
};

export default LcdContainer;

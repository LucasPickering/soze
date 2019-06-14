import makeUseResource from 'hooks/makeUseResource';
import { isEmpty } from 'lodash-es';
import React from 'react';
import { LcdSettings, Status } from 'state/types';
import LcdControls from './LcdControls';
import ResourceControlsContainer from './ResourceControlsContainer';

const useResource = makeUseResource<LcdSettings>('lcd');

interface Props {}

const LcdContainer: React.FC<Props> = () => {
  const {
    state: { loading, data, modifiedData },
    modifyData,
    saveData,
  } = useResource(Status.Normal);

  return (
    <ResourceControlsContainer
      title="LCD"
      loading={loading}
      modified={!isEmpty(modifiedData)}
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

import makeUseResource from 'hooks/makeUseResource';
import { isEmpty } from 'lodash-es';
import React from 'react';
import { LcdSettings, Status } from 'state/types';
import Lcd from './Lcd';
import Settings from './Settings';

const useResource = makeUseResource<LcdSettings>('lcd');

interface Props {}

const LcdContainer: React.FC<Props> = () => {
  const {
    state: { loading, data, modifiedData },
    modifyData,
    saveData,
  } = useResource(Status.Normal);

  return (
    <Settings
      title="LCD"
      loading={loading}
      modified={!isEmpty(modifiedData)}
      saveData={saveData}
    >
      {data ? (
        <Lcd
          settings={{
            ...data,
            ...modifiedData,
          }}
          modifyData={modifyData}
        />
      ) : null}
    </Settings>
  );
};

export default LcdContainer;

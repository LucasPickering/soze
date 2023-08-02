use crate::{
    resource::Resource,
    state::{hardware, user},
};

#[derive(Default)]
pub struct LcdResource;

impl Resource for LcdResource {
    type UserState = user::LcdState;
    type HardwareState = hardware::LcdState;

    fn get_user_state(
        global_state: &user::AllResourceState,
    ) -> &user::ResourceState<Self::UserState> {
        &global_state.lcd
    }

    fn get_user_state_mut(
        global_state: &mut user::AllResourceState,
    ) -> &mut user::ResourceState<Self::UserState> {
        &mut global_state.lcd
    }

    fn update(
        &mut self,
        user_state: &Self::UserState,
        hardware_state: &mut Self::HardwareState,
    ) {
        // TODO
    }
}

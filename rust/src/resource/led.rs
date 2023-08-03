use crate::{
    resource::Resource,
    state::{
        common::Color,
        hardware,
        user::{self, LedFadeState},
    },
};
use tokio::time::Instant;

/// RGB LEDs
pub struct LedResource {
    // Fade state
    color_index: usize,
    fade_start_time: Instant,
}

impl Default for LedResource {
    fn default() -> Self {
        Self {
            color_index: 0,
            fade_start_time: Instant::now(),
        }
    }
}

impl Resource for LedResource {
    type UserState = user::LedState;
    type HardwareState = hardware::LedState;

    fn get_user_state(
        global_state: &user::AllResourceState,
    ) -> &user::ResourceState<Self::UserState> {
        &global_state.led
    }

    fn get_user_state_mut(
        global_state: &mut user::AllResourceState,
    ) -> &mut user::ResourceState<Self::UserState> {
        &mut global_state.led
    }

    fn on_tick(
        &mut self,
        user_state: &Self::UserState,
        hardware_state: &mut Self::HardwareState,
    ) {
        // Update LED color
        hardware_state.color = match user_state.mode {
            user::LedMode::Off => Color::BLACK,
            user::LedMode::Static => user_state.static_.color,
            user::LedMode::Fade => {
                // Continually fade between colors, and roll over when we hit
                // the fade phase duration
                let LedFadeState {
                    colors, fade_time, ..
                } = &user_state.fade;

                if colors.is_empty() {
                    // Avoid divide-by-zero errors
                    Color::BLACK
                } else {
                    // If we've hit the end of this fade phase, tick over
                    let elapsed = Instant::elapsed(&self.fade_start_time);
                    if elapsed >= *fade_time {
                        self.color_index =
                            (self.color_index + 1) % colors.len();
                        self.fade_start_time = Instant::now();
                    }

                    // Interpolate between the two boundary colors based on time
                    let start_color = colors[self.color_index];
                    let end_color =
                        colors[(self.color_index + 1) % colors.len()];
                    let bias = elapsed.as_secs_f32() / fade_time.as_secs_f32();
                    start_color * (1.0 - bias) + end_color * bias
                }
            }
        };
    }
}

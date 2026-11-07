#include <assert.h>
#include <string.h>
#include "inktag_input_simulation.h"

int main(void) {
    inktag_input_simulation_t s = {0};
    uint8_t selector, action, payload[4];
    inktag_input_binding_t binding = {0, 5};
    assert(sizeof(s) == 8);
    for (selector = 0; selector < 4; ++selector) {
        for (action = 0; action <= 10; ++action) {
            bool valid = selector != 0 && action <= 9 && action != 8;
            binding.action = action;
            inktag_input_simulation_clear(&s);
            assert(inktag_input_simulation_begin(&s, 7, selector, &binding) ==
                (valid ? INKTAG_STATUS_OK : INKTAG_STATUS_UNSUPPORTED));
            if (!valid) { assert(s.phase == INKTAG_SIM_IDLE); continue; }
            assert(inktag_input_simulation_begin(&s, 8, selector, &binding) ==
                INKTAG_STATUS_BUSY);
            s.phase = INKTAG_SIM_DISPATCH;
            inktag_input_simulation_finish(&s, INKTAG_STATUS_OK);
            inktag_input_simulation_payload(&s, payload);
            assert(payload[0] == 4 && payload[1] == selector && payload[2] == action);
            assert(payload[3] == (action == 0 || action == 8 ? 0 : 1));
            assert(inktag_input_simulation_cancel(&s, 7, 8) == INKTAG_STATUS_NOT_FOUND);
        }
    }
    binding.action = 1;
    inktag_input_simulation_clear(&s);
    assert(inktag_input_simulation_begin(&s, 0, 0, &binding) == INKTAG_STATUS_INVALID_REQUEST);
    assert(inktag_input_simulation_begin(&s, 7, 4, &binding) == INKTAG_STATUS_INVALID_REQUEST);
    assert(inktag_input_simulation_begin(&s, 7, 0, NULL) == INKTAG_STATUS_INVALID_REQUEST);
    for (selector = 0; selector < 2; ++selector) {
        inktag_input_simulation_clear(&s);
        assert(inktag_input_simulation_begin(&s, 7, 1, &binding) == INKTAG_STATUS_OK);
        if (selector) s.phase = INKTAG_SIM_DISPATCH;
        assert(inktag_input_simulation_cancel(&s, 8, 9) == INKTAG_STATUS_NOT_FOUND);
        assert(inktag_input_simulation_cancel(&s, 7, 0) == INKTAG_STATUS_INVALID_REQUEST);
        assert(inktag_input_simulation_cancel(&s, 7, 7) == INKTAG_STATUS_INVALID_REQUEST);
        assert(inktag_input_simulation_cancel(&s, 7, 9) == INKTAG_STATUS_OK);
        if (selector) {
            assert(inktag_input_simulation_cancel(&s, 7, 10) == INKTAG_STATUS_BUSY);
            inktag_input_simulation_finish(&s, INKTAG_STATUS_OK);
        }
        assert(s.phase == INKTAG_SIM_TERMINAL_DRAIN);
        assert(s.status == INKTAG_STATUS_CANCELLED && s.outcome == 255);
        inktag_input_simulation_clear(&s); /* connection generation change */
        assert(inktag_input_simulation_cancel(&s, 7, 10) == INKTAG_STATUS_NOT_FOUND);
        assert(inktag_input_simulation_begin(&s, 7, 1, &binding) == INKTAG_STATUS_OK);
        inktag_input_simulation_finish(&s, INKTAG_STATUS_DENIED);
        assert(s.status == INKTAG_STATUS_DENIED && s.outcome == 255);
    }
    return 0;
}

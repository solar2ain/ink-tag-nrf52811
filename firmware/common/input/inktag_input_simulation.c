#include "inktag_input_simulation.h"
#include <string.h>

void inktag_input_simulation_clear(inktag_input_simulation_t *s) {
    memset(s, 0, sizeof(*s));
}

inktag_status_v2_t inktag_input_simulation_begin(
    inktag_input_simulation_t *s, uint8_t transaction, uint8_t selector,
    const inktag_input_binding_t *binding) {
    if (!transaction || selector > 3u || !binding)
        return INKTAG_STATUS_INVALID_REQUEST;
    if (s->phase != INKTAG_SIM_IDLE) return INKTAG_STATUS_BUSY;
    if (!inktag_input_action_allowed((inktag_input_source_t)(selector + 1u),
                                     binding->action))
        return INKTAG_STATUS_UNSUPPORTED;
    inktag_input_simulation_clear(s);
    s->phase = INKTAG_SIM_ACK_DRAIN;
    s->transaction = transaction;
    s->selector = selector;
    s->binding = *binding;
    return INKTAG_STATUS_OK;
}

inktag_status_v2_t inktag_input_simulation_cancel(
    inktag_input_simulation_t *s, uint8_t target, uint8_t cancel_transaction) {
    if (!target || !cancel_transaction || cancel_transaction == target)
        return INKTAG_STATUS_INVALID_REQUEST;
    if (target != s->transaction ||
        (s->phase != INKTAG_SIM_ACK_DRAIN && s->phase != INKTAG_SIM_DISPATCH))
        return INKTAG_STATUS_NOT_FOUND;
    if (s->cancel_transaction) return INKTAG_STATUS_BUSY;
    s->cancel_transaction = cancel_transaction;
    s->status = INKTAG_STATUS_CANCELLED;
    if (s->phase != INKTAG_SIM_DISPATCH)
        inktag_input_simulation_finish(s, INKTAG_STATUS_CANCELLED);
    return INKTAG_STATUS_OK;
}

void inktag_input_simulation_finish(inktag_input_simulation_t *s,
                                     inktag_status_v2_t status) {
    if (s->status != INKTAG_STATUS_CANCELLED) s->status = (uint8_t)status;
    s->outcome = s->status != INKTAG_STATUS_OK ? 0xffu :
        (s->binding.action == INKTAG_INPUT_ACTION_DISABLED ||
         s->binding.action == INKTAG_INPUT_ACTION_CONTROL_URL ? 0u : 1u);
    s->phase = INKTAG_SIM_TERMINAL_DRAIN;
}

void inktag_input_simulation_payload(const inktag_input_simulation_t *s,
                                      uint8_t payload[4]) {
    payload[0] = INKTAG_TEST_INPUT_SIMULATE;
    payload[1] = s->selector;
    payload[2] = s->binding.action;
    payload[3] = s->outcome;
}

#ifndef INKTAG_INPUT_SIMULATION_H
#define INKTAG_INPUT_SIMULATION_H

#include "inktag_input.h"
#include "inktag_protocol_v2.h"

enum {
    INKTAG_SIM_IDLE, INKTAG_SIM_ACK_DRAIN, INKTAG_SIM_DISPATCH,
    INKTAG_SIM_TERMINAL_DRAIN, INKTAG_SIM_TERMINAL_QUEUED
};

/* One connection-owned operation, never a physical input latch. Reset on every
 * connection generation change. Terminal capacity is four bytes, not a queue. */
typedef struct {
    uint8_t phase, transaction, selector;
    inktag_input_binding_t binding;
    uint8_t status, outcome, cancel_transaction;
} inktag_input_simulation_t;

void inktag_input_simulation_clear(inktag_input_simulation_t *state);
inktag_status_v2_t inktag_input_simulation_begin(
    inktag_input_simulation_t *state, uint8_t transaction, uint8_t selector,
    const inktag_input_binding_t *binding);
inktag_status_v2_t inktag_input_simulation_cancel(
    inktag_input_simulation_t *state, uint8_t target, uint8_t cancel_transaction);
void inktag_input_simulation_finish(inktag_input_simulation_t *state,
                                     inktag_status_v2_t status);
void inktag_input_simulation_payload(const inktag_input_simulation_t *state,
                                      uint8_t payload[4]);

#endif

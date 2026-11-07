#ifndef INKTAG_FREE_POLICY_H
#define INKTAG_FREE_POLICY_H

/* Permanent product boundary, independent of stored bytes and build options.
 * Allocated wire IDs remain in inktag_protocol_v2.h; no token/challenge,
 * entitlement object or logical image quota is part of this source port. */
#if INKTAG_NRF_ACTIVATION_ENABLED || INKTAG_NRF_FIND_ENABLED || INKTAG_NRF_PASSWORD_ENABLED
#error This_nRF52811_source_port_is_permanently_Free
#endif
#if defined(INKTAG_PROTOCOL_FREE_ONLY_TARGET) && !INKTAG_PROTOCOL_FREE_ONLY_TARGET
#error This_nRF52811_source_port_requires_Free_policy
#endif
#ifndef INKTAG_PROTOCOL_FREE_ONLY_TARGET
#define INKTAG_PROTOCOL_FREE_ONLY_TARGET 1
#endif


#if INKTAG_NRF_DEVICE_NAME_WRITABLE
#error This_nRF52811_source_port_preserves_factory_BLE_names
#endif
#endif

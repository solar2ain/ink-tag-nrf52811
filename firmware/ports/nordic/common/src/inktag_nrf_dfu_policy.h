#ifndef INKTAG_NRF_DFU_POLICY_H
#define INKTAG_NRF_DFU_POLICY_H

/* Public source builds permit unsigned application init packets. Official
 * production sets this explicitly to 1. A supplied signature is always checked. */
#ifndef INKTAG_NRF_REQUIRE_SIGNED_DFU
#define INKTAG_NRF_REQUIRE_SIGNED_DFU 0
#endif
#if INKTAG_NRF_REQUIRE_SIGNED_DFU != 0 && INKTAG_NRF_REQUIRE_SIGNED_DFU != 1
#error INKTAG_NRF_REQUIRE_SIGNED_DFU must be 0 or 1
#endif

/* Exact OP_PROTOCOL_VERSION response values, not a bit-field negotiation.
 * Both include the existing guarded ABORT/resume-app contract. */
#define INKTAG_NRF_DFU_PROTOCOL_SIGNED_REQUIRED 0x81u
#define INKTAG_NRF_DFU_PROTOCOL_UNSIGNED_ALLOWED 0xc1u
#if INKTAG_NRF_REQUIRE_SIGNED_DFU
#define INKTAG_NRF_DFU_RESUME_PROTOCOL INKTAG_NRF_DFU_PROTOCOL_SIGNED_REQUIRED
#else
#define INKTAG_NRF_DFU_RESUME_PROTOCOL INKTAG_NRF_DFU_PROTOCOL_UNSIGNED_ALLOWED
#endif

#endif

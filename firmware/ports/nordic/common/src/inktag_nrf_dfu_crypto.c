/* Minimal SHA-256 and P-256 verification used by Nordic Recovery. */
#include "inktag_nrf_dfu_crypto.h"

#include <stddef.h>
#include <string.h>

#include "nrf_error.h"
#include "sha256.h"
#include "uECC.h"

static bool sha256_le(uint8_t output[32], uint8_t const *data,
                      uint32_t length)
{
    sha256_context_t context;

    /* All three arguments are owned, non-null buffers here. Nordic's software
     * SHA implementation can fail only its public null-argument guards. */
    (void)sha256_init(&context);
    (void)sha256_update(&context, data, length);
    (void)sha256_final(&context, output, true);
    return true;
}

bool inktag_nrf_dfu_sha256_matches_le(uint8_t const expected[32],
                                      uint8_t const *data,
                                      uint32_t length)
{
    uint8_t actual[32];
    return sha256_le(actual, data, length) &&
           memcmp(actual, expected, sizeof(actual)) == 0;
}

bool inktag_nrf_dfu_p256_verify_le(uint8_t const public_key[64],
                                   uint8_t const signature[64],
                                   uint8_t const *data,
                                   uint32_t length)
{
    uint32_t hash_le_words[8];
    uint32_t signature_le_words[16];

    /* nrfutil stores both pk coordinates and both signature scalars in the
     * native little-endian representation selected for micro-ecc. The
     * protobuf signature may be byte-aligned, so copy it before passing it to
     * micro-ecc, which casts API byte arrays to native words in this mode. */
    memcpy(signature_le_words, signature, sizeof(signature_le_words));
    return sha256_le((uint8_t *)hash_le_words, data, length) &&
           uECC_verify(public_key, (uint8_t const *)hash_le_words,
                       sizeof(hash_le_words),
                       (uint8_t const *)signature_le_words,
                       uECC_secp256r1()) != 0;
}

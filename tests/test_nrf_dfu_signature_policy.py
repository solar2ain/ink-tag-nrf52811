"""Run the shipping SDK protobuf/admission code with real SHA256 and micro-ecc."""
import importlib.util
import hashlib
import io
import os
from pathlib import Path
import struct
import tempfile
import zipfile

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec, utils
from nrf_sdk_host import _compile_run, _function

ROOT = Path(__file__).resolve().parents[1]
SDK = Path(os.environ['INKTAG_NRF_SDK_ROOT'])


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def array(name, data):
    return 'static const uint8_t ' + name + '[]={' + ','.join(map(str, data)) + '};\n'


packer = load('packer', 'tools/ota/package-nrf52811.py')
app = struct.pack('<II', 0x20006000, 0x19009) + bytes(range(56))
archive, report = packer.package(app, 201)
assert not report['publisherVerified'] and report['firmwareVersion'] == 65737
assert archive == packer.package(app, 201)[0]
with zipfile.ZipFile(io.BytesIO(archive)) as z:
    unsigned = z.read('application.dat')
    assert z.read('application.bin') == app
# This fixture is short enough for single-byte message lengths. Check the
# actual SDK-decoded fields below, rather than trusting this extraction.
assert unsigned[:5] == bytes([10, len(unsigned)-2, 8, 1, 18])
init = unsigned[6:]
# Public, disposable fixture key; never an official signing key. Avoid d=2:
# that special point triggers exceptional additions in the SDK's co-Z verifier.
key = ec.derive_private_key(int.from_bytes(hashlib.sha256(
    b'InkTag public signature-policy test fixture').digest(), 'big'), ec.SECP256R1())
signature = bytes.fromhex(
    '09e387f2fd6f86baec0a4929bf6a33cad0348772eadaf047b6e18ac60a14e19a6'
    '290ada39dec06435aeeffedc74a3ff353319a81f30bda94b20b464f21a1dafb')
r, s = (int.from_bytes(signature[i:i+32], 'little') for i in (0, 32))
order = 0xffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551
# Independently verify both equivalent S forms before exercising the SDK.
for scalar in (s, order-s):
    key.public_key().verify(utils.encode_dss_signature(r, scalar), init, ec.ECDSA(hashes.SHA256()))
signed = packer.fields([(2, packer.fields([
    (1, packer.fields([(1, 1), (2, init)])), (2, 0),
    (3, r.to_bytes(32, 'little') + s.to_bytes(32, 'little'))]))])
alternate = packer.fields([(2, packer.fields([
    (1, packer.fields([(1, 1), (2, init)])), (2, 0),
    (3, r.to_bytes(32, 'little') + (order-s).to_bytes(32, 'little'))]))])
pub = key.public_key().public_numbers()
pk = pub.x.to_bytes(32, 'little') + pub.y.to_bytes(32, 'little')
for invalid in [b'', app[:-1], app + b'x' * 69632,
                struct.pack('<II', 0x20006008, 0x19009) + app[8:],
                struct.pack('<II', 0x20006000, 0x2a001) + app[8:]]:
    try:
        packer.package(invalid, 201)
    except ValueError:
        pass
    else:
        raise AssertionError('Unsafe App accepted')
for version in [-1, 65536, True]:
    try:
        packer.package(app, version)
    except ValueError:
        pass
    else:
        raise AssertionError('Invalid version accepted')

materializer = load('validation', 'tools/sdk/materialize-nordic-dfu-validation.py')
vendor = SDK / 'components/libraries/bootloader/dfu'
source = materializer.materialize(vendor / 'nrf_dfu_validation.c')
versions = (ROOT / 'firmware/ports/nordic/common/src/inktag_nrf_dfu_ver_validation.c').read_text(encoding='utf-8')
functions = '\n'.join(_function(source, declaration) for declaration in [
    'static void pb_decoding_callback(', 'static bool stored_init_cmd_decode(',
    'static nrf_dfu_result_t nrf_dfu_validation_signature_check(',
    'static bool signature_required(', 'nrf_dfu_result_t nrf_dfu_validation_prevalidate('])
version_functions = '\n'.join(_function(versions, declaration) for declaration in [
    'static bool softdevice_requirement_ok(',
    'nrf_dfu_result_t nrf_dfu_ver_validation_check('])
harness = r'''
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <string.h>
#include "pb_decode.h"
#include "pb_common.h"
#include "dfu-cc.pb.h"
#include "inktag_nrf_dfu_policy.h"
#include "inktag_nrf_dfu_crypto.h"
#include "inktag_nrf_dfu_epoch.h"
typedef unsigned nrf_dfu_result_t;
#define UNUSED_PARAMETER(x) (void)(x)
#define ASSERT(x) assert(x)
#define NRF_LOG_DEBUG(...)
#define NRF_LOG_ERROR(...)
#define NRF_LOG_WARNING(...)
#define NRF_LOG_HEXDUMP_DEBUG(...)
#define EXT_ERR(x) (0x100u+(x))
#define NRF_DFU_RES_CODE_SUCCESS 1u
#define NRF_DFU_RES_CODE_OPERATION_FAILED 10u
#define NRF_DFU_RES_CODE_INVALID_OBJECT 5u
#define NRF_DFU_EXT_ERROR_SIGNATURE_MISSING 1u
#define NRF_DFU_EXT_ERROR_WRONG_SIGNATURE_TYPE 2u
#define NRF_DFU_EXT_ERROR_INIT_COMMAND_INVALID 3u
#define NRF_DFU_EXT_ERROR_HW_VERSION_FAILURE 4u
#define NRF_DFU_EXT_ERROR_SD_VERSION_FAILURE 5u
#define NRF_DFU_EXT_ERROR_FW_VERSION_FAILURE 6u
#define NRF_DFU_HW_VERSION 52u
#define MBR_SIZE 4096u
#define SD_FWID_GET(x) 0x0126u
static dfu_packet_t m_packet;
static pb_istream_t m_pb_stream;
static dfu_init_command_t *mp_init;
static bool m_init_packet_valid;
static uint8_t *m_init_packet_data_ptr;
static uint32_t m_init_packet_data_len;
static struct {
    uint8_t init_command[512];
    struct {unsigned command_size;} progress;
    uint32_t app_version;
} s_dfu_settings;
''' + 'static uint32_t const pk_words[]={' + ','.join(str(x) for x in struct.unpack('<16I', pk)) + '};\n#define pk ((uint8_t const *)pk_words)\n'
harness += version_functions + '\n' + functions + '\n'
harness += array('unsigned_packet', unsigned) + array('signed_packet', signed)
harness += array('alternate_signed_packet', alternate)
harness += array('both_packet', unsigned + signed) + array('app', app)
harness += r'''
static bool decode(const uint8_t *p, unsigned n) {
    memcpy(s_dfu_settings.init_command,p,n);s_dfu_settings.progress.command_size=n;
    return stored_init_cmd_decode();
}
int main(void) {
    s_dfu_settings.app_version=0x10000u;
    assert(INKTAG_NRF_DFU_RESUME_PROTOCOL == (INKTAG_NRF_REQUIRE_SIGNED_DFU ? 0x81 : 0xc1));
    assert(decode(unsigned_packet,sizeof(unsigned_packet)));
    assert(!m_packet.has_signed_command && mp_init->fw_version==65737);
    assert(mp_init->hw_version==52 && mp_init->sd_req_count==1 && mp_init->sd_req[0]==294);
    assert(mp_init->has_type && mp_init->type==DFU_FW_TYPE_APPLICATION);
    assert(mp_init->app_size==sizeof(app) && mp_init->hash.hash_type==DFU_HASH_TYPE_SHA256);
    assert(mp_init->boot_validation_count==1 && mp_init->boot_validation[0].type==1);
    assert(mp_init->boot_validation[0].bytes.size==0);
    assert(inktag_nrf_dfu_sha256_matches_le(mp_init->hash.hash.bytes,app,sizeof(app)));
    assert(nrf_dfu_validation_prevalidate() == (INKTAG_NRF_REQUIRE_SIGNED_DFU ?
        EXT_ERR(NRF_DFU_EXT_ERROR_SIGNATURE_MISSING) : NRF_DFU_RES_CODE_SUCCESS));
    mp_init->hw_version=56;assert(nrf_dfu_ver_validation_check(mp_init)!=NRF_DFU_RES_CODE_SUCCESS);
    mp_init->hw_version=52;mp_init->sd_req[0]=0;assert(nrf_dfu_ver_validation_check(mp_init)!=NRF_DFU_RES_CODE_SUCCESS);
    mp_init->sd_req[0]=294;mp_init->fw_version=201;assert(nrf_dfu_ver_validation_check(mp_init)!=NRF_DFU_RES_CODE_SUCCESS);
    assert(decode(signed_packet,sizeof(signed_packet)));
    assert(m_packet.has_signed_command && nrf_dfu_validation_prevalidate()==NRF_DFU_RES_CODE_SUCCESS);
    assert(decode(alternate_signed_packet,sizeof(alternate_signed_packet)));
    assert(m_packet.has_signed_command && nrf_dfu_validation_prevalidate()==NRF_DFU_RES_CODE_SUCCESS);
    assert(decode(signed_packet,sizeof(signed_packet)));
    m_packet.signed_command.signature.bytes[0]^=1;
    assert(nrf_dfu_validation_prevalidate()==NRF_DFU_RES_CODE_INVALID_OBJECT);
    assert(decode(signed_packet,sizeof(signed_packet)));
    m_packet.signed_command.signature.size=63;
    assert(nrf_dfu_validation_prevalidate()==NRF_DFU_RES_CODE_OPERATION_FAILED);
    assert(decode(signed_packet,sizeof(signed_packet)));
    m_packet.signed_command.signature_type=DFU_SIGNATURE_TYPE_ED25519;
    assert(nrf_dfu_validation_prevalidate()==EXT_ERR(NRF_DFU_EXT_ERROR_WRONG_SIGNATURE_TYPE));
    assert(!decode(both_packet,sizeof(both_packet)));
    assert(!decode(unsigned_packet,sizeof(unsigned_packet)-1));
    assert(!decode(unsigned_packet,0));
    return 0;
}
'''
with tempfile.TemporaryDirectory() as directory:
    for mode in [0, 1]:
        _compile_run(Path(directory), 'policy-' + str(mode), harness,
            includes=('tests/mocks/nrf_crypto', 'firmware/ports/nordic/common/src',
                      str(vendor), str(SDK/'external/nano-pb'),
                      str(SDK/'components/libraries/sha256'),
                      str(SDK/'components/libraries/util'),
                      str(SDK/'components/softdevice/s112/headers'),
                      str(SDK/'external/micro-ecc/micro-ecc')),
            sources=('firmware/ports/nordic/common/src/inktag_nrf_dfu_crypto.c',
                     str(SDK/'components/libraries/sha256/sha256.c'),
                     str(SDK/'external/micro-ecc/micro-ecc/uECC.c'),
                     str(vendor/'dfu-cc.pb.c'),
                     str(SDK/'external/nano-pb/pb_common.c'),
                     str(SDK/'external/nano-pb/pb_decode.c')),
            defines=('-Wno-unused-function', '-Wno-unused-parameter',
                     f'-DINKTAG_NRF_REQUIRE_SIGNED_DFU={mode}', '-DuECC_WORD_SIZE=4',
                     '-DuECC_OPTIMIZATION_LEVEL=0', '-DuECC_VLI_NATIVE_LITTLE_ENDIAN=1',
                     '-DuECC_SUPPORTS_secp160r1=0', '-DuECC_SUPPORTS_secp192r1=0',
                     '-DuECC_SUPPORTS_secp224r1=0', '-DuECC_SUPPORTS_secp256k1=0',
                     '-DuECC_SUPPORTS_secp256r1=1'))
print('PASS both shipping SDK policies: unsigned, real signed P256, bad signature/type/length, ambiguous/truncated packets, target/epoch, deterministic package and vector bounds')

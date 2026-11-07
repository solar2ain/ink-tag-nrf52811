"""Exercise real Make entry routing without signing or accessing hardware."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
VARIABLE = 'INKTAG_NRF_REQUIRE_SIGNED_DFU'
BASE_ENV = {k: v for k, v in os.environ.items()
            if k not in ('MAKEFLAGS', 'MFLAGS', 'MAKEOVERRIDES', VARIABLE)}


def make(entry, *args, env=None, success=True):
    result = subprocess.run(['make', '-f', entry, *args], cwd=ROOT,
                            env=env or BASE_ENV, capture_output=True, text=True)
    if success:
        assert result.returncode == 0, result.stderr
    else:
        assert result.returncode != 0, result.stdout
        assert 'requires INKTAG_NRF_REQUIRE_SIGNED_DFU=1' in result.stderr, result.stderr
    return result


def profile(entry, *args):
    text = make(entry, 'print-build-profile', *args).stdout
    return dict(line.split('=', 1) for line in text.splitlines() if '=' in line)


# The one-command target preserves the same public profile and signed input.
for entry, expected in [('Makefile', 'optional'), ('Makefile.signed', 'required')]:
    command = make(entry, '-n', 'full', 'SIGNED_OTA=matching.zip').stdout
    assert 'python3 build.py --profile '+expected in command, command
    assert '--signed-ota "matching.zip"' in command, command


optional = profile('Makefile')
required = profile('Makefile.signed')
assert optional['signatureRequired'] == '0' and optional['profile'] == 'optional'
assert required['signatureRequired'] == '1' and required['profile'] == 'required'
assert optional['build'] != required['build'] and optional['output'] != required['output']
assert required['signing'] == optional['signing'] == 'no'
for entry, value in [('Makefile', '0'), ('Makefile.signed', '1')]:
    p = profile(entry, 'BUILD_DIR=custom-cache', 'OUTPUT_DIR=custom-output',
                'NRF_SIGNATURE_PROFILE=spoofed', 'NRF_PROFILE_OUTPUT_DIR=spoofed')
    suffix = 'required' if value == '1' else 'optional'
    assert p['build'] == 'custom-cache/' + suffix
    assert p['output'] == 'custom-output/' + suffix
    assert p['signatureRequired'] == value
for entry in ['Makefile.signed'] + (['Makefile.private'] if (ROOT/'Makefile.private').exists() else []):
    for bad in ['0', '2', '']:
        make(entry, VARIABLE+'='+bad, success=False)
        make(entry, env={**BASE_ENV, VARIABLE: bad}, success=False)
    make(entry, env={**BASE_ENV, VARIABLE: '0', 'MAKEFLAGS': '-e'}, success=False)
for field in ['CFLAGS', 'ASFLAGS']:
    a=['make', '-f', 'firmware/ports/nordic/nrf52811/bootloader/Makefile',
       'print-delivery-config', VARIABLE+'=1', field+'=-D'+VARIABLE+'=0']
    r=subprocess.run(a, cwd=ROOT, env=BASE_ENV, capture_output=True, text=True)
    assert r.returncode and 'not compiler flags' in r.stderr
r=subprocess.run(['make','-f','Makefile.signed','nrf52811-aesl-ota'],
                 cwd=ROOT, env=BASE_ENV, capture_output=True, text=True)
assert r.returncode and 'Unsigned OTA packaging requires' in r.stderr

if (ROOT/'Makefile.private').exists():
    # Substitute only the Python executable. The real private Make recipe runs
    # a harmless argv recorder, never the actual build/sign/delivery pipeline.
    with tempfile.TemporaryDirectory() as directory:
        tmp=Path(directory);stub=tmp/'recorder.py';output=tmp/'record.json'
        stub.write_text('import sys,os,json\nfrom pathlib import Path\n'
            'Path(os.environ["ENTRY_RECORD"]).write_text(json.dumps({"argv":sys.argv[1:],'
            '"policy":os.environ.get("INKTAG_NRF_REQUIRE_SIGNED_DFU")}))\n',encoding='utf-8')
        make('Makefile.private', 'nrf52811-aesl', 'PYTHON='+sys.executable+' '+str(stub),
             env={**BASE_ENV,'ENTRY_RECORD':str(output)})
        row=json.loads(output.read_text(encoding='utf-8'))
        assert row['policy']=='1' and row['argv'][0]=='tools/delivery/normal_build.py'
        assert '--scope' not in row['argv']  # Official default is the normal signing producer.
    sys.path.insert(0,str(ROOT/'tools/delivery'))
    spec=importlib.util.spec_from_file_location('normal_build',ROOT/'tools/delivery/normal_build.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    valid='CFLAGS=-Oz -D'+VARIABLE+'=1\nASFLAGS=-D'+VARIABLE+'=1\n'
    module.require_signed_recovery_config(valid)
    for invalid in ['', valid.replace('=1','=0'),valid.replace('CFLAGS=', 'CFLAGS=-D'+VARIABLE+'=0 '),
                    valid.replace('ASFLAGS=-D'+VARIABLE+'=1','ASFLAGS=-g')]:
        try:module.require_signed_recovery_config(invalid)
        except ValueError:pass
        else:raise AssertionError('Official admission accepted absent/duplicate/optional flags')
    before=os.environ.get(VARIABLE)
    os.environ[VARIABLE]='0'
    try:
        try:module._pipeline(None)
        except ValueError as error:assert 'Official producer requires' in str(error)
        else:raise AssertionError('Direct official producer accepted optional environment')
    finally:
        if before is None:os.environ.pop(VARIABLE,None)
        else:os.environ[VARIABLE]=before

print('PASS real optional/required Make routes, isolated paths, CLI/environment/compiler downgrade rejection and private pre-signing admission')

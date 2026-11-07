"""Permanent Free build policy rejects attempts to restore positive engines."""
import os, subprocess, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory() as directory:
    source=Path(directory)/'policy.c'; source.write_text('#include "inktag_free_policy.h"\nint main(void){return !INKTAG_PROTOCOL_FREE_ONLY_TARGET;}\n')
    for define in (None,'INKTAG_NRF_ACTIVATION_ENABLED=1','INKTAG_NRF_FIND_ENABLED=1',
                   'INKTAG_NRF_PASSWORD_ENABLED=1','INKTAG_PROTOCOL_FREE_ONLY_TARGET=0','INKTAG_NRF_DEVICE_NAME_WRITABLE=1'):
        binary=Path(directory)/'policy'
        result=subprocess.run([os.environ.get('CC','cc'),'-std=c99','-Ifirmware/common/protocol',
                  *(['-D'+define] if define else []),str(source),'-o',str(binary)],cwd=ROOT,capture_output=True)
        assert (result.returncode==0)==(define is None),(define,result.stderr)
        if define is None:subprocess.run([str(binary)],check=True)
        else:assert b'This_nRF52811_source_port' in result.stderr
print('PASS permanent Free policy and five rejected positive configurations')

# Export closure physically excludes unused engines, independently of LTO.
import json,re
policy=json.loads((ROOT/'tools/source/free-source-allowlist.json').read_text())
audit_name='protocol/common-free-projection.json'
assert audit_name not in policy['files']
if (ROOT/'source-export.json').is_file():
    assert not (ROOT/audit_name).exists()
# An accidental allowlist addition must fail before internal audit data is read.
import runpy
select=runpy.run_path(str(ROOT/'tools/source/export-free.py'))['selected']
with tempfile.TemporaryDirectory() as directory:
    isolated=Path(directory);(isolated/'tools/source').mkdir(parents=True)
    (isolated/'tools/source/free-source-allowlist.json').write_text(json.dumps({'files':[audit_name]}))
    try:
        select(isolated)
    except ValueError as error:
        assert 'Unsafe export path' in str(error)
    else:
        raise AssertionError('Internal audit file was allowed into public source')
for stem in ('nfc_binding','nfc_link','nfc_command','ndef','type2_uri_store','type4_ndef','gt_mirror'):
    for suffix in ('c','h'):
        name='firmware/common/input/inktag_'+stem+'.'+suffix
        assert not (ROOT/name).exists(),name
        assert name not in policy['files'],name
source=(ROOT/'firmware/common/epd/inktag_epd_ssd.c').read_text()
for symbol in ('SSD1675_154_FULL_LUT','SSD1677_426_GRAY4_LUT'):
    assert symbol not in source
private=re.compile(rb'ink[-_]tag[-_](?:main|nrf52811|da14585)|[A-Za-z]:[/\\]Projects[/\\]',re.I)
for name in policy['files']:
    assert not private.search((ROOT/name).read_bytes()),name
print('PASS physical Free closure and neutral public provenance')

# Public Free sources contain no uploadable-font codec or excluded screen engines.
for name in ('inktag_gui_asset_package.c','inktag_gui_asset_package.h'):
    assert not (ROOT/'firmware/common/gui'/name).exists()
for name in ('inktag_epd_e6.inc',):
    assert not (ROOT/'firmware/common/epd'/name).exists()
with tempfile.TemporaryDirectory() as directory:
    source=Path(directory)/'screens.c'
    source.write_text('#include "inktag_epd_screen.h"\nint main(void){return 0;}\n')
    for name in ('UC8151','UC8159','SSD1675','SSD1677_GRAY4','JD79665CA','OSPREY_E6'):
        result=subprocess.run([os.environ.get('CC','cc'),'-std=c99','-Ifirmware/common/epd',
                '-DINKTAG_EPD_ENABLE_'+name+'=1',str(source),'-o',str(Path(directory)/'screens')],cwd=ROOT,capture_output=True)
        assert result.returncode and b'This_nRF52811_source_port_excludes_' in result.stderr,name
print('PASS absent unsupported implementations and six rejected screen build configurations')

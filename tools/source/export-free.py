"""Copy an explicit Free source allowlist into a fresh local directory."""
import argparse, hashlib, json, shutil, re
from pathlib import Path, PurePosixPath
ROOT = Path(__file__).resolve().parents[2]
FORBIDDEN = {'.git','.local','.sdk','.tools','.secrets','AGENTS.md','Makefile.private','factory_backups',
             'common-free-projection.json'}

def selected(root):
    policy = json.loads((root/'tools/source/free-source-allowlist.json').read_text())
    names = policy['files']
    if names != sorted(set(names)):
        raise ValueError('Allowlist must be sorted and unique')
    for name in names:
        parts = PurePosixPath(name).parts
        if not parts or parts[0].endswith(':') or PurePosixPath(name).is_absolute() or '..' in parts or set(parts)&FORBIDDEN or '\\' in name:
            raise ValueError('Unsafe export path: '+name)
        path = root/name
        for ancestor in [path, *path.parents]:
            if ancestor == root: break
            if ancestor.is_symlink() or (hasattr(ancestor,'is_junction') and ancestor.is_junction()):
                raise ValueError('Linked export input: '+name)
        if not path.is_file(): raise ValueError('Missing input: '+name)
        private = re.compile(rb'ink[-_]tag[-_](?:main|nrf52811|da14585)|[A-Za-z]:[/\\]Projects[/\\]', re.I)
        if private.search(path.read_bytes()):raise ValueError('Private provenance in export input: '+name)
    return names

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('destination',type=Path)
    args=parser.parse_args(); destination=args.destination.absolute()
    names=selected(ROOT)
    destination.mkdir(parents=True,exist_ok=False)
    records={}
    for name in names:
        data=(ROOT/name).read_bytes(); out=destination/name
        out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data)
        records[name]={'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
    manifest={'schemaVersion':1,'buildTarget':'nrf52811_aesl','unsigned':True,
              'publicationApproved':False,'rightsStatus':'third-party terms retained; see NOTICE.md and THIRD_PARTY_NOTICES.md',
              'files':records}
    (destination/'source-export.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({'files':len(records),'destination':str(destination),'publicationApproved':False}))
if __name__=='__main__':main()

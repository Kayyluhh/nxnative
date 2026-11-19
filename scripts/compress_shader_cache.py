#!/usr/bin/env python3
"""Compress a build folder's shader compile cache (<title ID>_build/shader/cache/cas-*.db), or make it raw again with --decompress. No game build runs, and nothing is compiled again.
The NSP script's --compress-shader-cache keeps it compressed from then on; a compressed file stays so whatever later builds are told. Each file is written anew beside the old one and
replaces it when whole: the drive needs the compressed size free while it runs. Refused while a build uses the cache."""
import argparse, os, sqlite3, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'dm/tools'))
import shader_cache


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('build_folder', type=Path, help='a <title ID>_build folder, or its shader/cache folder')
    ap.add_argument('--decompress', action='store_true', help='make the cache raw again (what code from before compression reads)')
    ap.add_argument('--workers', type=int, default=os.cpu_count() or 1, help='threads that compress (default: every core)')
    a = ap.parse_args(argv)
    folder = a.build_folder.expanduser()
    if (folder / 'shader/cache').is_dir(): folder = folder / 'shader/cache'
    if not shader_cache.generations(folder):
        print(f'[RED] no shader compile cache in {folder}', file=sys.stderr); return 1
    try: done = shader_cache.convert_folder(folder, not a.decompress, workers=a.workers)
    except (OSError, RuntimeError, sqlite3.Error) as e:
        print(f'[RED] shader compile cache: {e}', file=sys.stderr); return 1
    if not done: print(f'already {"raw" if a.decompress else "compressed"}: {folder}')
    else: print(f'{sum(b for _, (b, _) in done) / 1e9:.2f} → {sum(x for _, (_, x) in done) / 1e9:.2f} GB in {len(done)} file{"s" if len(done) > 1 else ""}')
    return 0


if __name__ == '__main__': sys.exit(main())

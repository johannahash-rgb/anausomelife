#!/usr/bin/env python3
"""Compatibility entry point for the site's existing edition builder."""
import argparse, importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('glossary_v2',HERE/'glossary_v2.py')
core=importlib.util.module_from_spec(spec);spec.loader.exec_module(core)

def build(root):
    root=Path(root)
    core.build(root)
    css=root/'assets/caregiver-glossary.css'
    if css.exists():
        source=css.read_text()
        marker='/* No-JavaScript layout */'
        if marker not in source:
            source+='\n'+marker+'\n.cg-root:not(.cg-enhanced) .cg-workspace{display:block}.cg-root:not(.cg-enhanced) .cg-start nav{display:none!important}\n'
            css.write_text(source)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,default=Path('.'))
    build(parser.parse_args().root)

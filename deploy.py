#!/usr/bin/env python3

import argparse
import subprocess
import os

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('dirs', nargs='+', help="Directories to sync")
    parser.add_argument('host', help="Destination host")
    parser.add_argument('--target-dir', '-t', default='soze', help="Destination directory")
    args = parser.parse_args()

    curdir = os.path.dirname(os.path.realpath(__file__))
    gitignore_path = os.path.join(curdir, '.gitignore')

    cmd = [
        'rsync', '-av',
        f'--exclude-from={gitignore_path}',  # Exclude files in .gitignore
        *args.dirs,
        f'{args.host}:{args.target_dir}'
    ]

    print(' '.join(cmd))
    subprocess.call(cmd)

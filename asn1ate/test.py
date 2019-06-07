#!/usr/bin/env python

# Copyright (c) 2013-2019, Schneider Electric Buildings AB
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of Schneider Electric Buildings AB nor the
#       names of contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from __future__ import print_function  # Python 2 compatibility

import os
import sys
import argparse  # Requires Python 2.7 or later, but that's OK for a test driver
from asn1ate import parser, sema, pyasn1gen


def parse_args():
    ap = argparse.ArgumentParser(description='Test driver for asn1ate.')
    ap.add_argument('file', help='ASN.1 file to test.')
    ap.add_argument('--outdir',
                    help='Write Python module files to directory instead of stdout')
    ap.add_argument('--include-asn1', action='store_true',
                    help='Pass --include-asn1 to code generator')

    # Actions
    group = ap.add_mutually_exclusive_group(required=True)
    group.add_argument('--parse', action='store_true',
                       help='Only parse.')
    group.add_argument('--sema', action='store_true',
                       help='Only parse and build semantic model')
    group.add_argument('--gen', action='store_true',
                       help='Parse, build semantic model and generate pyasn1 code (default)')

    return ap.parse_args()


def generate_module_code(args):
    # Absolutize input path before changing working directory
    infile = os.path.abspath(args.file)
    split = bool(args.outdir)

    prev_cwd = os.getcwd()
    try:
        if split:
            os.chdir(args.outdir)

        pyasn1gen.main(argparse.Namespace(file=infile, split=split,
                                          include_asn1=args.include_asn1))
    finally:
        os.chdir(prev_cwd)


# Simplistic command-line driver
def main():
    args = parse_args()
    with open(args.file) as f:
        asn1def = f.read()

    if args.outdir and not args.gen:
        print('ERROR: can only use --outdir with --gen', file=sys.stderr)
        return 1

    parse_tree = parser.parse_asn1(asn1def)
    if args.parse:
        parser.print_parse_tree(parse_tree)
        return 0

    modules = sema.build_semantic_model(parse_tree)
    if args.sema:
        for module in modules:
            print(module)
        return 0

    if args.gen:
        generate_module_code(args)

    return 0


if __name__ == '__main__':
    sys.exit(main())

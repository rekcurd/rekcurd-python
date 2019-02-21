# -*- coding: utf-8 -*-


import argparse

from .startapp_handler import startapp_handler
from rekcurd import _version


def create_parser():
    parser = argparse.ArgumentParser(description='rekcurd command')
    parser.add_argument(
        '--version', '-v', action='version', version=_version.__version__)
    subparsers = parser.add_subparsers()

    # startapp
    parser_startapp = subparsers.add_parser(
        'startapp', help='see `rekcurd startapp -h`')
    parser_startapp.add_argument(
        'name', help='Name of the application or project.')
    parser_startapp.add_argument(
        '--dir', required=False, help='Optional destination directory', default='./')
    parser_startapp.set_defaults(handler=startapp_handler)

    return parser


def main() -> None:
    parser = create_parser()
    args = parser.parse_args()

    if hasattr(args, 'handler'):
        args.handler(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()

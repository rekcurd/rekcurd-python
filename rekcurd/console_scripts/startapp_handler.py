# -*- coding: utf-8 -*-


import os
import rekcurd
import shutil
import stat

from pathlib import Path

from .errors import CommandError


def _make_writeable(filename):
    """
    Make sure that the file is writeable.
    Useful if our source is read-only.
    """
    if not os.access(filename, os.W_OK):
        st = os.stat(filename)
        new_permissions = stat.S_IMODE(st.st_mode) | stat.S_IWUSR
        os.chmod(filename, new_permissions)


def startapp_handler(args):
    if Path(args.name).name != args.name:
        raise TypeError("Invalid project name: "+args.name)
    destination = Path(args.dir, args.name)
    if destination.exists():
        raise CommandError("'{}' already exists".format(destination.absolute()))
    destination.mkdir(parents=True, exist_ok=False)

    base_name = "RekcurdAppTemplate"
    template_suffix = "-tpl"
    template_dir = Path(rekcurd.__path__[0], 'template')

    for root, dirs, files in os.walk(template_dir):
        for dirname in dirs[:]:
            if dirname.startswith('.') or dirname == '__pycache__':
                dirs.remove(dirname)

        for filename in files:
            if filename.endswith(('.pyo', '.pyc', '.py.class')):
                # Ignore some files as they cause various breakages.
                continue
            old_path = Path(root, filename)
            new_path = Path(destination, filename)
            if str(new_path).endswith(template_suffix):
                new_path = Path(str(new_path)[:-len(template_suffix)])

            if new_path.exists():
                raise CommandError("{} already exists, overlaying a "
                                   "project into an existing directory"
                                   "won't replace conflicting files".format(new_path))

            with old_path.open(mode='r', encoding='utf-8') as template_file:
                content = template_file.read().replace(base_name, args.name)
            with new_path.open(mode='w', encoding='utf-8') as new_file:
                new_file.write(content)

            try:
                shutil.copymode(str(old_path), str(new_path))
                _make_writeable(str(new_path))
            except OSError:
                print(
                    "Notice: Couldn't set permission bits on {}. You're "
                    "probably using an uncommon filesystem setup. No "
                    "problem.".format(new_path)
                )

#!/usr/bin/env python3

# for linux install: "python3 setup.py install --prefix=/usr --exec-prefix=/usr -f"

from distutils.core import setup
from distutils.dist import Distribution
from distutils.cmd import Command
from distutils.command.install_data import install_data
from distutils.command.install import install
from distutils.command.build import build
from distutils.dep_util import newer
from distutils.log import warn, info, error
from distutils.errors import DistutilsFileError

import os, glob, sys, subprocess
import builtins
def _(transl_str):
    return transl_str
builtins._ = _
sys.path.append(os.path.join(os.getcwd(), "modules"))
import cons

PO_DIR = 'locale'
MO_DIR = os.path.join('build', 'mo')


class XTileDist(Distribution):
    global_options = Distribution.global_options + [
       ("without-gettext", None, "Don't build/install gettext .mo files") ]

    def __init__ (self, *args):
        self.without_gettext = False
        Distribution.__init__(self, *args)


class BuildData(build):
    def run(self):
        build.run(self)
        xtile_man_file = "linux/x-tile.1"
        xtile_man_file_gz = xtile_man_file + ".gz"
        if newer(xtile_man_file, xtile_man_file_gz):
            if os.path.isfile(xtile_man_file_gz): os.remove(xtile_man_file_gz)
            import gzip
            f_in = open(xtile_man_file, 'rb')
            f_out = gzip.open(xtile_man_file_gz, 'wb')
            f_out.writelines(f_in)
            f_out.close()
            f_in.close()
        if self.distribution.without_gettext: return
        for po in glob.glob(os.path.join (PO_DIR, '*.po')):
            lang = os.path.basename(po[:-3])
            mo = os.path.join(MO_DIR, lang, 'x-tile.mo')
            directory = os.path.dirname(mo)
            if not os.path.exists(directory):
                info('creating %s' % directory)
                os.makedirs(directory)
            if newer(po, mo):
                info('compiling %s -> %s' % (po, mo))
                try:
                    rc = subprocess.call(['msgfmt', '-o', mo, po])
                    if rc != 0: raise Warning("msgfmt returned %d" % rc)
                except Exception as e:
                    error("Building gettext files failed. Try setup.py --without-gettext [build|install]")
                    error("Error: %s" % str(e))
                    sys.exit(1)


class Uninstall(Command):
    description = "Attempt an uninstall from an install --record file"
    user_options = [('manifest=', None, 'Installation record filename')]

    def initialize_options(self):
        self.manifest = None

    def finalize_options(self):
        pass

    def get_command_name(self):
        return 'uninstall'

    def run(self):
        f = None
        self.ensure_filename('manifest')
        try:
            try:
                if not self.manifest:
                    raise DistutilsFileError("Pass manifest with --manifest=file")
                f = open(self.manifest)
                files = [file.strip() for file in f]
            except IOError as e:
                raise DistutilsFileError("unable to open install manifest: %s", str(e))
        finally:
            if f: f.close()
        for file in files:
            if os.path.isfile(file) or os.path.islink(file):
                info("removing %s" % repr(file))
                if not self.dry_run:
                    try: os.unlink(file)
                    except OSError as e:
                        warn("could not delete: %s" % repr(file))
            elif not os.path.isdir(file):
                info("skipping %s" % repr(file))
        dirs = set()
        for file in reversed(sorted(files)):
            dir = os.path.dirname(file)
            if dir not in dirs and os.path.isdir(dir) and len(os.listdir(dir)) == 0:
                dirs.add(dir)
                # Only nuke empty Python library directories, else we could destroy
                # e.g. locale directories we're the only app with a .mo installed for.
                if dir.find("site-packages/") > 0:
                    info("removing %s" % repr(dir))
                    if not self.dry_run:
                        try: os.rmdir(dir)
                        except OSError as e:
                            warn("could not remove directory: %s" % str(e))
                else: info("skipping empty directory %s" % repr(dir))


class Install(install):
    def run(self):
        self.distribution.scripts=['x-tile']
        install.run(self)


class InstallData(install_data):
    def run(self):
        self.data_files.extend(self._find_mo_files())
        self.data_files.extend(self._find_desktop_file())
        install_data.run(self)

    def _find_desktop_file(self):
        return [("share/applications", ["linux/x-tile.desktop"] )]

    def _find_mo_files(self):
        data_files = []
        if not self.distribution.without_gettext:
            for mo in glob.glob(os.path.join (MO_DIR, '*', 'x-tile.mo')):
                lang = os.path.basename(os.path.dirname(mo))
                dest = os.path.join('share', 'locale', lang, 'LC_MESSAGES')
                data_files.append((dest, [mo]))
        return data_files


setup(
    name = "X Tile",
    description = "Tile the Windows Upon Your X Desktop",
    long_description = "Allows you to select a number of windows and tile them in different ways",
    version = cons.VERSION,
    author = "Giuseppe Penone & Chris Camacho",
    author_email = "giuspen@gmail.com & chris@bedroomcoders.co.uk",
    url = "http://www.giuspen.com/x-tile/",
    license = "GPL",
    data_files = [
                  ("share/icons/hicolor/scalable/apps", ["glade/x-tile.svg"] ),
                  ("share/x-tile/glade", glob.glob("glade/*.*") ),
                  ("share/x-tile/modules", glob.glob("modules/*.py") ),
                  ("share/man/man1", ["linux/x-tile.1.gz"]) ],
    cmdclass={
        'build': BuildData,
        'install_data': InstallData,
        'install': Install,
        'uninstall': Uninstall
      },
    distclass=XTileDist
)

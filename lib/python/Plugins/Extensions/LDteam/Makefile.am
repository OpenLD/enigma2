installdir = $(pkglibdir)/python/Plugins/Extensions/LDteam

SUBDIRS = images scripts

install_PYTHON = *.py

dist_install_DATA = sundtekinstall.sh

install-data-hook:
        @chmod +x $(DESTDIR)$(installdir)/sundtekinstall.sh


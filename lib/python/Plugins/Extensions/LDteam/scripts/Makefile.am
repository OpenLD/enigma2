installdir = $(pkglibdir)/python/Plugins/Extensions/LDteam/scripts

install_PYTHON = *.sh

dist_install_DATA = *.sh

install-data-hook:
        @chmod +x $(DESTDIR)$(installdir)/*.sh

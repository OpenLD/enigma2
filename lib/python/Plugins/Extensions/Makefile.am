installdir = $(pkglibdir)/python/Plugins/Extensions

SUBDIRS = LDteam OpenIPTV TuxboxPlugins CutListEditor PicturePlayer MediaScanner MediaPlayer SocketMMI DVDBurn Modem Volume_adjust ProgrammlistenUpdater RemoteStreamConverter

if HAVE_LIBDDVD
SUBDIRS += DVDPlayer
endif

if VUSOLO4K
SUBDIRS += MiniTV
endif

install_PYTHON = __init__.py

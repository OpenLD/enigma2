AM_CPPFLAGS = \
	-include Python.h

AM_CXXFLAGS = \
	-Wall \
	-fno-exceptions

plugindir = $(libdir)/enigma2/python/Components/Converter

plugin_LTLIBRARIES = libbitratecalc.la

libbitratecalc_la_SOURCES = \
	bitratecalc.cpp \
	bitratecalc.h

libbitratecalc_la_LIBADD = \
	@LIBCRYPTO_LIBS@


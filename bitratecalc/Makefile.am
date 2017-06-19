AM_CPPFLAGS = \
	-include Python.h

AM_CXXFLAGS = \
	-Wall \
	-fno-exceptions

libdir = $(libdir)/enigma2/python/Components/Converter

lib_LTLIBRARIES = libbitratecalc.la

libbitratecalc_la_SOURCES = \
	bitratecalc.cpp \
	bitratecalc.h

libbitratecalc_la_LIBADD = \
	@LIBCRYPTO_LIBS@


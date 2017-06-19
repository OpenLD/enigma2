AM_CPPFLAGS = \
	-include Python.h

AM_CXXFLAGS = \
	-Wall \
	-fno-exceptions

libdir = $(libdir)/enigma2/python/Components/Converter

lib_LTLIBRARIES = bitratecalc.la

bitratecalc_la_SOURCES = \
	bitratecalc.cpp \
	bitratecalc.h

bitratecalc_la_LIBADD = \
	@LIBCRYPTO_LIBS@


#ifndef __lib_gdi_palette_h
#define __lib_gdi_palette_h

#if !defined(SWIG)

#include <lib/gdi/rgba.h>
#include <lib/gdi/color.h>
#include <vector>

class gPalette
{
	gRGBA m_invalidColor;
	std::vector<gRGBA> m_colorTable;

public:
	void setColorCount(unsigned int colorCount)
	{
		m_colorTable.resize(colorCount);
	}

	void setColor(unsigned int index, const gRGBA &colorValue)
	{
		if (index < colorCount())
			m_colorTable[index] = colorValue;
	}

	void setColorTable(const std::vector<gRGBA> &colors)
	{
		m_colorTable = colors;
	}

	gPalette()
	{
	}

	gPalette(const gPalette &p) :
		m_colorTable(p.m_colorTable)
	{
	}

	gColor findColor(const gRGBA &rgb) const;

	const gRGBA &color(unsigned int index) const
	{
		if (index < colorCount())
			return m_colorTable[index];

		return m_invalidColor;
	}

	unsigned int colorCount() const
	{
		return m_colorTable.size();
	}

	std::vector<gRGBA> colorTable() const
	{
		return m_colorTable;
	}
};

struct gLookup
{
	int size;
	gColor *lookup;
	gLookup(int size, const gPalette &pal, const gRGBA &start, const gRGBA &end);
	gLookup();
	~gLookup() { delete [] lookup; }
	void build(int size, const gPalette &pal, const gRGBA &start, const gRGBA &end);
};

#endif /* !SWIG */

#endif /* __lib_gdi_palette_h */

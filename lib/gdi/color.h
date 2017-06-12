#ifndef __lib_gdi_color_h
#define __lib_gdi_color_h

#if !defined(SWIG)

struct gColor
{
	unsigned int color;
	gColor(unsigned int color): color(color)
	{
	}
	gColor(): color(0)
	{
	}
	operator unsigned int() const { return color; }
	bool operator==(const gColor &o) const { return o.color==color; }
};

#endif /* !SWIG */

#endif /* __lib_gdi_color_h */

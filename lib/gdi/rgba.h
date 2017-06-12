#ifndef __lib_gdi_rgba_h
#define __lib_gdi_rgba_h

#include <lib/gdi/gpixelformat.h>

class gRGBA
{
	unsigned int a8() const;
	unsigned int gray8() const;
	unsigned int rgba4444() const;
	unsigned int argb4444() const;
	unsigned int bgra4444() const;
	unsigned int abgr4444() const;
	unsigned int rgba5551() const;
	unsigned int argb1555() const;
	unsigned int bgra5551() const;
	unsigned int abgr1555() const;
	unsigned int rgb565() const;
	unsigned int bgr565() const;
	unsigned int rgb888() const;
	unsigned int bgr888() const;
	unsigned int rgba8888() const;
	unsigned int argb8888() const;
	unsigned int bgra8888() const;
	unsigned int abgr8888() const;
	unsigned int customFormat(gPixelFormat fmt) const;

public:
	unsigned char r;
	unsigned char g;
	unsigned char b;
	unsigned char a;

	gRGBA(unsigned int r, unsigned int g, unsigned int b, unsigned int a = 0xff) :
		r(r), g(g), b(b), a(a)
	{
	}

	gRGBA() :
		r(0), g(0), b(0), a(0xff)
	{
	}

	unsigned int argb() const
	{
		return (a << 24) | (r << 16) | (g << 8) | b;
	}

	static gRGBA fromArgb(unsigned int c)
	{
		return gRGBA((c >> 16) & 0xff, (c >> 8) & 0xff, c & 0xff, (c >> 24) & 0xff);
	}

	bool operator<(const gRGBA &c) const
	{
		if (b < c.b)
			return 1;
		if (b == c.b)
		{
			if (g < c.g)
				return 1;
			if (g == c.g)
			{
				if (r < c.r)
					return 1;
				if (r == c.r)
					return a < c.a;
			}
		}
		return 0;
	}
	bool operator==(const gRGBA &c) const
	{
		return (b == c.b) && (g == c.g) && (r == c.r) && (a == c.a);
	}
	bool operator!=(const gRGBA &c) const
	{
		return (b != c.b) || (g != c.g) || (r != c.r) || (a != c.a);
	}

	static unsigned long premultiplyChannel(unsigned long c, unsigned long a)
	{
		// c * a / 255
		c *= a;
		c += 128;
		return ((c >> 8) + c) >> 8;
	}

	gRGBA premultiplyAlpha() const
	{
		if (a == 0xff)
			return *this;
		return gRGBA(premultiplyChannel(r, a),
			    premultiplyChannel(g, a),
			    premultiplyChannel(b, a),
			    a);
	}

	void set(unsigned int _r, unsigned int _g, unsigned int _b)
	{
		r = _r;
		g = _g;
		b = _b;
	}

	void set(unsigned int _r, unsigned int _g, unsigned int _b, unsigned int _a)
	{
		r = _r;
		g = _g;
		b = _b;
		a = _a;
	}

	// Returns a pixel in native endian format. But 24-bpp is always big-endian.
	unsigned int pixel(gPixelFormat fmt) const;
	void fromPixel(gPixelFormat fmt, unsigned int pixel);
};

//
// gRGB exists for backwards compatibility. It stores
// inverse alpha values. You should use gRGBA instead.
//
class gRGB : public gRGBA
{
public:
	class gRGBuchar
	{
		unsigned char *m_parent;
		unsigned char m_val;

		void update();

	public:
		gRGBuchar(unsigned char *parent);

		operator int() const;
		int operator=(int val);
		int operator+=(int val);
	};

	gRGBuchar a;

	gRGB(int _r, int _g, int _b, int _a = 0);
	gRGB(unsigned int val);
	gRGB();

	void operator=(unsigned int argb);
	unsigned int argb() const;
};

#endif /* __lib_gdi_rgba_h */

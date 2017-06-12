#ifndef __gpixelformat_h
#define __gpixelformat_h

#include <string>

//
// Bit layout of gPixelFormat:
//
//   28   24   20   16   12    8   5     0
// RRRR GGGG BBBB AAAA rrrr FFFF TTT bbbbb
//
// R = 4 bits: number of red or Y bits [0..15]
// G = 4 bits: number of green or U (Cb) bits [0..15]
// B = 4 bits: number of blue or V (Cr) bits [0..15]
// A = 4 bits: number of alpha or don't care bits [0..15]
// r = 4 bits: reserved [= 0]
// F = 4 bits: type specific flags
// T = 3 bits: type [0..7]
// b = 5 bits: bits per pixel minus 1 [0..31]
//
// types: RGB=0, Palette=1, Gray=2, Alpha=3, YUV=4
//
// Specific flags for RGB:
//  bit 0: has alpha: 0=no 1=yes
//  bit 1: color order: 0=RGB, 1=BGR
//  bit 2: alpha position: 0=MSB, 1=LSB
//
// Specific bits for Palette:
//  None
//
// Specific bits for Grey:
//  None
//
// Specific bits for Alpha:
//  None
//
// Specific flags for YUV:
//  bit 0: has alpha: 0=no 1=yes
//  bit 1: color order: 0=RGB, 1=BGR
//  bit 2: alpha position: 0=MSB, 1=LSB
//  bit 3: format: 0=packed, 1=planar
//

#define __PIXEL_FMT_SHIFT_SIZE_R	28
#define __PIXEL_FMT_MASK_SIZE_R		0x0f
#define __PIXEL_FMT_SHIFT_SIZE_G	24
#define __PIXEL_FMT_MASK_SIZE_G		0x0f
#define __PIXEL_FMT_SHIFT_SIZE_B	20
#define __PIXEL_FMT_MASK_SIZE_B		0x0f
#define __PIXEL_FMT_SHIFT_SIZE_A	16
#define __PIXEL_FMT_MASK_SIZE_A		0x0f
#define __PIXEL_FMT_SHIFT_FLAGS		8
#define __PIXEL_FMT_MASK_FLAGS		0x0f
#define __PIXEL_FMT_SHIFT_TYPE		5
#define __PIXEL_FMT_MASK_TYPE		0x07
#define __PIXEL_FMT_SHIFT_BPP		0
#define __PIXEL_FMT_MASK_BPP		0x1f

#define __PIXEL_FMT_FLAG_RGB_BYTE_ORDER_RGB	(0 << 0)
#define __PIXEL_FMT_FLAG_RGB_BYTE_ORDER_BGR	(1 << 0)
#define __PIXEL_FMT_FLAG_RGB_ALPHA_FIRST	(0 << 1)
#define __PIXEL_FMT_FLAG_RGB_ALPHA_LAST		(1 << 1)
#define __PIXEL_FMT_FLAG_RGB_NO_ALPHA		(0 << 2)
#define __PIXEL_FMT_FLAG_RGB_HAS_ALPHA		(1 << 2)

#define __PIXEL_FMT_FLAG_YUV_BYTE_ORDER_YUV	(0 << 0)
#define __PIXEL_FMT_FLAG_YUV_BYTE_ORDER_YVU	(1 << 0)
#define __PIXEL_FMT_FLAG_YUV_ALPHA_FIRST	(0 << 1)
#define __PIXEL_FMT_FLAG_YUV_ALPHA_LAST		(1 << 1)
#define __PIXEL_FMT_FLAG_YUV_NO_ALPHA		(0 << 2)
#define __PIXEL_FMT_FLAG_YUV_HAS_ALPHA		(1 << 2)
#define __PIXEL_FMT_FLAG_YUV_PACKED		(0 << 3)
#define __PIXEL_FMT_FLAG_YUV_PLANAR		(1 << 3)

#define __PIXEL_FMT_MASK(name)		__PIXEL_FMT_MASK_##name
#define __PIXEL_FMT_SHIFT(name)		__PIXEL_FMT_SHIFT_##name
#define __PIXEL_FMT_FLAG_RGB(name)	__PIXEL_FMT_FLAG_RGB_##name
#define __PIXEL_FMT_FLAG_YUV(name)	__PIXEL_FMT_FLAG_YUV_##name

#define __PIXEL_FMT_SET_COMPONENT(name, value)	\
	(((value) & __PIXEL_FMT_MASK(name)) << __PIXEL_FMT_SHIFT(name))

#define __PIXEL_FMT_GET_COMPONENT(fmt, name)	\
	(unsigned long)(((fmt) >> __PIXEL_FMT_SHIFT(name)) & __PIXEL_FMT_MASK(name))

enum {
	__PIXEL_FMT_TYPE_RGB = 0,
	__PIXEL_FMT_TYPE_PALETTE = 1,
	__PIXEL_FMT_TYPE_GRAY = 2,
	__PIXEL_FMT_TYPE_ALPHA = 3,
	__PIXEL_FMT_TYPE_YUV = 4,
};

#define __PIXEL_FMT_RGB_TEMPLATE(sr, sg, sb, sa, byte_order, alpha_pos, has_alpha) \
	__PIXEL_FMT_SET_COMPONENT(SIZE_R, sr) | \
	__PIXEL_FMT_SET_COMPONENT(SIZE_G, sg) | \
	__PIXEL_FMT_SET_COMPONENT(SIZE_B, sb) | \
	__PIXEL_FMT_SET_COMPONENT(SIZE_A, sa) | \
	__PIXEL_FMT_SET_COMPONENT(FLAGS, \
		__PIXEL_FMT_FLAG_RGB(byte_order) | \
		__PIXEL_FMT_FLAG_RGB(alpha_pos) | \
		__PIXEL_FMT_FLAG_RGB(has_alpha)) | \
	__PIXEL_FMT_SET_COMPONENT(TYPE, __PIXEL_FMT_TYPE_RGB) | \
	__PIXEL_FMT_SET_COMPONENT(BPP, sr + sg + sb + sa - 1)

#define E_PIXEL_FMT_RGB(sr, sg, sb, byte_order) \
	__PIXEL_FMT_RGB_TEMPLATE(sr, sg, sb, 0, byte_order, ALPHA_FIRST, NO_ALPHA)

#define E_PIXEL_FMT_RGBA(sr, sg, sb, sa, byte_order, alpha_pos) \
	__PIXEL_FMT_RGB_TEMPLATE(sr, sg, sb, sa, byte_order, alpha_pos, HAS_ALPHA)

#define E_PIXEL_FMT_RGBX(sr, sg, sb, sa, byte_order, alpha_pos) \
	__PIXEL_FMT_RGB_TEMPLATE(sr, sg, sb, sa, byte_order, alpha_pos, NO_ALPHA)

#define E_PIXEL_FMT_PALETTE(bpp) \
	__PIXEL_FMT_SET_COMPONENT(TYPE, __PIXEL_FMT_TYPE_PALETTE) | \
	__PIXEL_FMT_SET_COMPONENT(BPP, bpp - 1)

#define E_PIXEL_FMT_ALPHA(bpp) \
	__PIXEL_FMT_SET_COMPONENT(TYPE, __PIXEL_FMT_TYPE_ALPHA) | \
	__PIXEL_FMT_SET_COMPONENT(BPP, bpp - 1)

#define E_PIXEL_FMT_GRAY(bpp) \
	__PIXEL_FMT_SET_COMPONENT(TYPE, __PIXEL_FMT_TYPE_GRAY) | \
	__PIXEL_FMT_SET_COMPONENT(BPP, bpp - 1)

#define __PIXEL_FMT_YUV_TEMPLATE(sy, su, sv, sa, byte_order, alpha_pos, has_alpha, planar) \
	__PIXEL_FMT_SET_COMPONENT(SIZE_R, sy) | \
	__PIXEL_FMT_SET_COMPONENT(SIZE_G, su) | \
	__PIXEL_FMT_SET_COMPONENT(SIZE_B, sv) | \
	__PIXEL_FMT_SET_COMPONENT(SIZE_A, sa) | \
	__PIXEL_FMT_SET_COMPONENT(FLAGS, \
		__PIXEL_FMT_FLAG_YUV(byte_order) | \
		__PIXEL_FMT_FLAG_YUV(alpha_pos) | \
		__PIXEL_FMT_FLAG_YUV(has_alpha) | \
		__PIXEL_FMT_FLAG_YUV(planar)) | \
	__PIXEL_FMT_SET_COMPONENT(TYPE, __PIXEL_FMT_TYPE_YUV) | \
	__PIXEL_FMT_SET_COMPONENT(BPP, sy + su + sv + sa - 1)

#define E_PIXEL_FMT_YUV(sy, su, sv, byte_order, planar) \
	__PIXEL_FMT_YUV_TEMPLATE(sy, su, sv, 0, byte_order, ALPHA_FIRST, NO_ALPHA, planar)

// All multi-channel pixel formats are big-endian, i.e. correspond to the
// order of bytes stored in memory.
class gPixel {
public:
	enum Channel {
		R,
		Y = R,
		G,
		U = G,
		Cb = U,
		B,
		V = B,
		Cr = V,
		A,
		X = A,
	};

	enum Format {
		ANY = 0,

		A_8 = E_PIXEL_FMT_ALPHA(8),
		GRAY_8 = E_PIXEL_FMT_GRAY(8),
		PALETTE_8 = E_PIXEL_FMT_PALETTE(8),

		RGBX_4444 = E_PIXEL_FMT_RGBX(4, 4, 4, 4, BYTE_ORDER_RGB, ALPHA_LAST),
		XRGB_4444 = E_PIXEL_FMT_RGBX(4, 4, 4, 4, BYTE_ORDER_RGB, ALPHA_FIRST),
		BGRX_4444 = E_PIXEL_FMT_RGBX(4, 4, 4, 4, BYTE_ORDER_BGR, ALPHA_LAST),
		XBGR_4444 = E_PIXEL_FMT_RGBX(4, 4, 4, 4, BYTE_ORDER_BGR, ALPHA_FIRST),

		RGBA_4444 = E_PIXEL_FMT_RGBA(4, 4, 4, 4, BYTE_ORDER_RGB, ALPHA_LAST),
		ARGB_4444 = E_PIXEL_FMT_RGBA(4, 4, 4, 4, BYTE_ORDER_RGB, ALPHA_FIRST),
		BGRA_4444 = E_PIXEL_FMT_RGBA(4, 4, 4, 4, BYTE_ORDER_BGR, ALPHA_LAST),
		ABGR_4444 = E_PIXEL_FMT_RGBA(4, 4, 4, 4, BYTE_ORDER_BGR, ALPHA_FIRST),

		RGBX_5551 = E_PIXEL_FMT_RGBX(5, 5, 5, 1, BYTE_ORDER_RGB, ALPHA_LAST),
		XRGB_1555 = E_PIXEL_FMT_RGBX(5, 5, 5, 1, BYTE_ORDER_RGB, ALPHA_FIRST),
		BGRX_5551 = E_PIXEL_FMT_RGBX(5, 5, 5, 1, BYTE_ORDER_BGR, ALPHA_LAST),
		XBGR_1555 = E_PIXEL_FMT_RGBX(5, 5, 5, 1, BYTE_ORDER_BGR, ALPHA_FIRST),

		RGBA_5551 = E_PIXEL_FMT_RGBA(5, 5, 5, 1, BYTE_ORDER_RGB, ALPHA_LAST),
		ARGB_1555 = E_PIXEL_FMT_RGBA(5, 5, 5, 1, BYTE_ORDER_RGB, ALPHA_FIRST),
		BGRA_5551 = E_PIXEL_FMT_RGBA(5, 5, 5, 1, BYTE_ORDER_BGR, ALPHA_LAST),
		ABGR_1555 = E_PIXEL_FMT_RGBA(5, 5, 5, 1, BYTE_ORDER_BGR, ALPHA_FIRST),

		RGB_565 = E_PIXEL_FMT_RGB(5, 6, 5, BYTE_ORDER_RGB),
		BGR_565 = E_PIXEL_FMT_RGB(5, 6, 5, BYTE_ORDER_BGR),

		RGB_888 = E_PIXEL_FMT_RGB(8, 8, 8, BYTE_ORDER_RGB),
		BGR_888 = E_PIXEL_FMT_RGB(8, 8, 8, BYTE_ORDER_BGR),

		RGBX_8888 = E_PIXEL_FMT_RGBX(8, 8, 8, 8, BYTE_ORDER_RGB, ALPHA_LAST),
		XRGB_8888 = E_PIXEL_FMT_RGBX(8, 8, 8, 8, BYTE_ORDER_RGB, ALPHA_FIRST),
		BGRX_8888 = E_PIXEL_FMT_RGBX(8, 8, 8, 8, BYTE_ORDER_BGR, ALPHA_LAST),
		XBGR_8888 = E_PIXEL_FMT_RGBX(8, 8, 8, 8, BYTE_ORDER_BGR, ALPHA_FIRST),

		RGBA_8888 = E_PIXEL_FMT_RGBA(8, 8, 8, 8, BYTE_ORDER_RGB, ALPHA_LAST),
		ARGB_8888 = E_PIXEL_FMT_RGBA(8, 8, 8, 8, BYTE_ORDER_RGB, ALPHA_FIRST),
		BGRA_8888 = E_PIXEL_FMT_RGBA(8, 8, 8, 8, BYTE_ORDER_BGR, ALPHA_LAST),
		ABGR_8888 = E_PIXEL_FMT_RGBA(8, 8, 8, 8, BYTE_ORDER_BGR, ALPHA_FIRST),

		YUV_NV12 = E_PIXEL_FMT_YUV(8, 8, 8, BYTE_ORDER_YUV, PLANAR),
		YUV_NV21 = E_PIXEL_FMT_YUV(8, 8, 8, BYTE_ORDER_YVU, PLANAR),
	};

	static unsigned long bitsPerPixel(Format fmt);
	static unsigned long bytesPerPixel(Format fmt);
	static unsigned long size(Format fmt, Channel c);

	static unsigned long byteOffset(Format fmt, Channel c);
	static unsigned long shift(Format fmt, Channel c);

	static unsigned int fromRGBA(Format fmt, unsigned long r, unsigned long g, unsigned long b, unsigned long a, unsigned long bitsPerChannel = 8);
	static void toRGBA(Format fmt, unsigned int pixel, unsigned long *r, unsigned long *g, unsigned long *b, unsigned long *a, unsigned long bitsPerChannel = 8);
	static bool isGray(Format fmt);
	static bool isAlphaFirst(Format fmt);
	static bool isBgr(Format fmt);
	static bool hasAlpha(Format fmt);
	static bool isIndexed(Format fmt);
	static bool isPlanar(Format fmt);

	static Format createFormat(unsigned long rsize, unsigned long gsize, unsigned long bsize, unsigned long asize, bool isBgr, bool alphaLast, bool hasAlpha);
	static Format alphaPixelFormat(Format fmt);
	static inline Format preferredFormat() { return g_preferredFormat; }
	static void setPreferredFormat(Format fmt) { g_preferredFormat = fmt; }

	static std::string name(Format fmt);

private:
	static Format g_preferredFormat;
	static const enum Channel *byteOrder(unsigned long flags);
};

typedef gPixel::Format gPixelFormat;

#endif /* __gpixelformat_h */

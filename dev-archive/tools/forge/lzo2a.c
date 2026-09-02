/* lzo2a.c - LZO2A block decompressor, transcribed from LZO's lzo2a_d.ch with
 * the config2a.h build constants (SWD_N 8191 -> no M3 branch, M1_MIN_LEN 2,
 * LZO_EOF_CODE).  Built as a tiny shared library for forge.py's ctypes path.
 *
 *   clang -O2 -shared -o lzo2a.dll lzo2a.c
 *
 * Returns the number of output bytes written, or a negative error:
 *   -1 input overrun, -2 output overrun, -3 lookbehind underrun,
 *   -4 EOF marker not found, -5 input not fully consumed.
 * *consumed receives the number of input bytes read.
 */
#include <stddef.h>
#include <stdint.h>

#ifdef _WIN32
#define EXPORT __declspec(dllexport)
#else
#define EXPORT
#endif

EXPORT long lzo2a_decompress(const uint8_t *in, size_t in_len,
                             uint8_t *out, size_t out_len, size_t *consumed)
{
    const uint8_t *ip = in, *ip_end = in + in_len;
    uint8_t *op = out, *op_end = out + out_len;
    const uint8_t *m_pos;
    uint32_t b = 0;
    unsigned k = 0;
    size_t t;

#define NEEDBITS(n) do { if (k < (n)) { if (ip >= ip_end) goto in_ovr; \
                          b |= (uint32_t)(*ip++) << k; k += 8; } } while (0)
#define MASKBITS(n) (b & ((1u << (n)) - 1))
#define DUMPBITS(n) do { b >>= (n); k -= (n); } while (0)

    while (ip < ip_end) {
        NEEDBITS(1);
        if (MASKBITS(1) == 0) {
            DUMPBITS(1);
            if (ip >= ip_end) goto in_ovr;
            if (op >= op_end) goto out_ovr;
            *op++ = *ip++;
            continue;
        }
        DUMPBITS(1);
        NEEDBITS(1);
        if (MASKBITS(1) == 0) {
            DUMPBITS(1);
            NEEDBITS(2);
            t = 2 + MASKBITS(2);
            DUMPBITS(2);
            if (ip >= ip_end) goto in_ovr;
            m_pos = op - 1 - *ip++;
            if (m_pos < out) goto lb_ovr;
            if (op + t > op_end) goto out_ovr;
            while (t--) *op++ = *m_pos++;
            continue;
        }
        DUMPBITS(1);
        if (ip + 2 > ip_end) goto in_ovr;
        t = *ip++;
        m_pos = op - ((t & 31) | ((size_t)(*ip++) << 5));
        t >>= 5;
        if (t == 0) {
            t = 10 - 1;
            if (ip >= ip_end) goto in_ovr;
            while (*ip == 0) { t += 255; ip++; if (ip >= ip_end) goto in_ovr; }
            t += *ip++;
        } else {
            if (m_pos == op) goto eof_found;
            t += 2;
        }
        if (m_pos < out) goto lb_ovr;
        if (op + t > op_end) goto out_ovr;
        while (t--) *op++ = *m_pos++;
    }
    *consumed = (size_t)(ip - in);
    return -4;
eof_found:
    *consumed = (size_t)(ip - in);
    if (ip != ip_end) return -5;
    return (long)(op - out);
in_ovr:  *consumed = (size_t)(ip - in); return -1;
out_ovr: *consumed = (size_t)(ip - in); return -2;
lb_ovr:  *consumed = (size_t)(ip - in); return -3;
}

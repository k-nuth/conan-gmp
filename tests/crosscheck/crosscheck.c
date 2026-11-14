/* Copyright (c) 2016-present Knuth Project developers.
   Distributed under the MIT software license, see the accompanying
   file COPYING or http://www.opensource.org/licenses/mit-license.php.

   Runs a fixed sequence of integer operations and prints a digest of every
   result. Operands and results cross the library boundary as bytes, so the
   digest does not depend on the limb size: two builds of GMP that compute the
   same values print the same line, whatever their target. */

#include <gmp.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

static uint64_t state = 88172645463325252ULL;

static uint64_t next(void) {
    state ^= state << 13;
    state ^= state >> 7;
    state ^= state << 17;
    return state;
}

static uint64_t digest = 14695981039346656037ULL;

static void absorb_byte(unsigned char byte) {
    digest ^= byte;
    digest *= 1099511628211ULL;
}

static void absorb(mpz_t const value) {
    static unsigned char buffer[8192];
    size_t count = 0;
    size_t i;
    if ((mpz_sizeinbase(value, 2) + 7) / 8 > sizeof buffer) {
        fprintf(stderr, "result too large\n");
        exit(1);
    }
    mpz_export(buffer, &count, -1, 1, -1, 0, value);
    absorb_byte(mpz_sgn(value) < 0 ? 1 : 0);
    absorb_byte((unsigned char)(count & 0xff));
    absorb_byte((unsigned char)(count >> 8));
    for (i = 0; i < count; ++i) absorb_byte(buffer[i]);
}

static void random_value(mpz_t value, size_t bytes, int may_be_negative) {
    static unsigned char buffer[1024];
    size_t i;
    for (i = 0; i < bytes; ++i) buffer[i] = (unsigned char)next();
    buffer[bytes - 1] |= 0x01; /* exactly `bytes` long, never zero */
    mpz_import(value, bytes, -1, 1, -1, 0, buffer);
    if (may_be_negative && (next() & 1)) mpz_neg(value, value);
}

int main(void) {
    static size_t const sizes[] = {1, 3, 4, 5, 7, 8, 9, 15, 16, 17, 31, 32, 33, 63, 64, 65,
                                   127, 128, 129, 255, 256, 257, 511, 512, 513, 1000};
    size_t const size_count = sizeof sizes / sizeof sizes[0];
    mpz_t a, b, c, q, r, t;
    int round;
    mpz_inits(a, b, c, q, r, t, NULL);

    for (round = 0; round < 4000; ++round) {
        size_t const a_bytes = sizes[next() % size_count];
        size_t const b_bytes = sizes[next() % size_count];
        size_t const c_bytes = sizes[next() % size_count];
        random_value(a, a_bytes, 1);
        random_value(b, b_bytes, 1);
        random_value(c, c_bytes, 0);

        mpz_add(t, a, b); absorb(t);
        mpz_sub(t, a, b); absorb(t);
        mpz_mul(t, a, b); absorb(t);
        mpz_mul(t, a, a); absorb(t);
        mpz_tdiv_qr(q, r, a, b); absorb(q); absorb(r);
        mpz_fdiv_qr(q, r, a, c); absorb(q); absorb(r);
        mpz_mul(t, a, b); mpz_tdiv_qr(q, r, t, c); absorb(q); absorb(r);
        mpz_gcd(t, a, b); absorb(t);
        mpz_abs(t, a); mpz_sqrtrem(q, r, t); absorb(q); absorb(r);
        mpz_mul_2exp(t, a, (mp_bitcnt_t)(next() % 200)); absorb(t);
        mpz_tdiv_q_2exp(t, a, (mp_bitcnt_t)(next() % 200)); absorb(t);
        mpz_and(t, a, b); absorb(t);
        mpz_ior(t, a, b); absorb(t);
        mpz_xor(t, a, b); absorb(t);
        absorb_byte((unsigned char)(mpz_cmp(a, b) > 0 ? 2 : mpz_cmp(a, b) < 0 ? 1 : 0));
        if (round % 16 == 0) {
            mpz_abs(t, a);
            mpz_setbit(c, 0); /* odd modulus */
            mpz_abs(q, b);
            mpz_powm(r, t, q, c); absorb(r);
            if (mpz_invert(r, t, c) != 0) absorb(r);
        }
        if (round % 64 == 0) {
            char* const text = mpz_get_str(NULL, 10, a);
            char const* p;
            for (p = text; *p != 0; ++p) absorb_byte((unsigned char)*p);
            mpz_set_str(t, text, 10);
            absorb(t);
            free(text);
        }
    }

    mpz_clears(a, b, c, q, r, t, NULL);
    printf("%016llx\n", (unsigned long long)digest);
    return 0;
}

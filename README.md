# GMP Conan recipe

Knuth-maintained packaging of **GMP 6.3.0**, based on the recipe of Conan
Center Index (CCI). The package stays `gmp/6.3.0`, with CCI's options, defaults
and CMake targets (`gmp::libgmp`, `gmp::gmpxx`), so consumers need no change
beyond taking this recipe revision.

Only the latest GMP release is packaged: `recipes/gmp/config.yml` lists one
version, and the patches of older releases are not carried.

## What differs from CCI

Native builds are CCI's. The difference is the WebAssembly (Emscripten) build:

- **64-bit limbs.** GMP sizes its limbs after `unsigned long`, which is 32 bits
  in WebAssembly, although the machine has 64-bit integers. The recipe
  configures `ABI=longlong`, so a limb is an `unsigned long long`.
- **Native double-limb multiplication.** GMP's generic C code multiplies two
  limbs out of four half-limb products. A patch to `longlong.h` uses the
  compiler's 128-bit integer instead (and, for 32-bit limbs, 64-bit integers
  for both multiplication and division).

`mp_limb_t` is therefore 64 bits wide under Emscripten. Code that passes
numbers as bytes or through the `mpz_*` interface is not affected; code that
assumes `sizeof(mp_limb_t) == sizeof(long)` is.

Time per operation under Node.js, Emscripten 6.0.13, same operands:

| Operation | CCI recipe | This recipe |
| --- | --- | --- |
| 32-byte × 32-byte multiply | 292 ns | 88 ns |
| 64-byte / 32-byte divide and modulo | 401 ns | 144 ns |
| 256-byte × 256-byte multiply | 10.2 µs | 2.7 µs |
| 512-byte / 256-byte divide and modulo | 15.7 µs | 3.4 µs |

The multiplication thresholds in `patches/emscripten/0002-gmp-mparam.h.patch`
are CCI's, tuned for 32-bit limbs. They have not been tuned again.

## Build and verify

With Conan 2.34.0 and CMake 4.4.4:

```sh
conan profile detect
conan create recipes/gmp/all --version 6.3.0 -s compiler.cppstd=23 \
  --build='gmp/*' -o 'gmp/*:run_checks=True'
conan test tests/crosscheck gmp/6.3.0 -s compiler.cppstd=23
```

`run_checks=True` runs GMP's own test suite during the build.

`tests/crosscheck` runs a fixed sequence of operations (arithmetic, division,
GCD, square roots, shifts, bitwise operations, modular exponentiation and
inversion, decimal conversion) on operands from 1 to 1000 bytes and compares a
digest of every result with `tests/crosscheck/expected.txt`. Numbers cross the
library boundary as bytes, so the digest is the same for every target and limb
size: a build that computes a different value anywhere fails.

For WebAssembly, add the Emscripten toolchain recipe and use the profile; the
cross-check then runs on Node.js:

```sh
git clone https://github.com/conan-io/conan-toolchains.git
conan remote add conan-toolchains ./conan-toolchains
conan create recipes/gmp/all --version 6.3.0 -pr:h profiles/emscripten -pr:b default --build='gmp/*' --build=missing
conan test tests/crosscheck gmp/6.3.0 -pr:h profiles/emscripten -pr:b default
```

GMP's own test suite cannot run in that build, which is why the cross-check
exists.

CI builds the package and runs the cross-check with the project toolchains:

| Runner | Compiler | GMP test suite |
| --- | --- | --- |
| Ubuntu 24.04 | GCC 16 | yes |
| macOS 26 | Xcode 26.6 / Apple Clang 21 | yes |
| Windows 2025 | VS 2026 / MSVC toolset 14.44 (Conan 194) | no |
| Ubuntu 24.04 | Emscripten 6.0.13 | no |

## Track CCI changes

`upstream/gmp` is the pristine import of CCI's recipe, with all its versions;
`upstream.json` records the CCI commit it was taken from. It is reference
material: the published recipe is under `recipes/gmp`.

```sh
python scripts/compare-upstream.py --ref master
```

This read-only tool shows what changed in CCI since the recorded commit,
followed by the local changes. Review both, apply what is wanted to
`recipes/gmp`, and update `upstream/gmp` and `upstream.json` together.

## Add a new GMP release

1. Replace the version in `recipes/gmp/config.yml` and
   `recipes/gmp/all/conandata.yml`, with the checksum of the official archive.
   Do not keep the previous version.
2. Check that every patch still applies, in particular
   `patches/emscripten/0003-longlong.h-wide-primitives.patch`.
3. Run the package build and the cross-check for every target above. The
   expected digest does not change with the GMP version.

## Publish

When a push to `main` passes the whole matrix, CI uploads the recipe to the
Knuth package remote (`https://packages.kth.cash/api/`). Only the recipe is
uploaded: each consumer builds GMP with its own profile. The job summary shows
the published recipe revision, which is what a consumer pins.

The job needs the `CONAN_LOGIN_USERNAME` and `CONAN_3_PASSWORD` secrets.
Nothing here changes the version pins of the consumers.

Recipe code keeps CCI's MIT license. GMP is distributed under LGPL-3.0 or
GPL-2.0; its license files are included in the packages.

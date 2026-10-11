# Linked math library

The browser build links nine math objects from the existing WASI SDK 34 archive:
`sin`, `cos`, `__sin`, `__cos`, `__rem_pio2`, `__rem_pio2_large`, `scalbn`,
`atan`, and `atan2`.
These are platform math routines, not recovered THUG2 source. No WASI system
services are linked. The build manifest records the archive and object hashes.

The SDK's `wasi-libc` submodule is pinned to
[`2e6fb9d8ee0cdf9e431fbcabe8af3115de000a13`](https://github.com/WebAssembly/wasi-libc/tree/2e6fb9d8ee0cdf9e431fbcabe8af3115de000a13).
The routines come from its `libc-top-half/musl/src/math` directory.

Preserve [musl's copyright/license](licenses/musl-COPYRIGHT.txt) and the
[per-file math notices](licenses/fdlibm-NOTICES.txt) with distributions that include
these routines. `__rem_pio2` also credits optimization by Bruce D. Evans.

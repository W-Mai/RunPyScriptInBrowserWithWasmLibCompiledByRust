#!/usr/bin/env bash

cargo build --release --target wasm32-unknown-unknown
cp target/wasm32-unknown-unknown/release/run_py_script_in_browser_with_wasm_lib.wasm web/test.wasm
#wasm-bindgen web/test.wasm --out-dir web/

#!/usr/bin/env bash

cargo build --release --target wasm32-unknown-unknown
cp target/wasm32-unknown-unknown/release/RunPyScriptInBrowserWithWasmLib.wasm web/test.wasm
#wasm-bindgen web/test.wasm --out-dir web/

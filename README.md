# Run PyScript In Browser With Wasm Lib Compiled By Rust

## 1. Install Rust

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
rustup target add wasm32-unknown-unknown
```

## 2. Build Wasm Lib

```bash
./build.sh
```

## 3. Run Server

```bash
cd web
python -m http.server
```

## 4. Open Browser

Open `http://localhost:8000` in browser, and you will see the result.

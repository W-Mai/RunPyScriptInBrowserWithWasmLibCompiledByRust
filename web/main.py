import sys
import ctypes
from pyscript import display, window, document
from js import wasm_exports, Array, Uint8Array, Int32Array, Uint32Array, Blob, URL

display(sys.version)

def get_buff(ptr):
    arr = Uint32Array.new(wasm_exports.memory.buffer, ptr)
    return (arr[0], arr[1])

# https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/ArrayBuffer
def deal_a_buffer(buf):
    display(f"deal a buffer")
    buf_len = buf.byteLength
    array_ptr = wasm_exports.alloc_memory(buf_len)
    array_view = Uint8Array.new(wasm_exports.memory.buffer, array_ptr)
    array_view.set(Uint8Array.new(buf))
    res = wasm_exports.deal_image(array_ptr, buf_len)
    display(f"array_ptr: {array_ptr} buf_len: {buf_len} deal: {res}")
    (img_buff, img_len) = get_buff(res)
    display(f"img_buff: {img_buff} img_len: {img_len}")
    img_view = Uint8Array.new(wasm_exports.memory.buffer, img_buff, img_len)

    blob = Blob.new( [img_view] );
    objectURL = URL.createObjectURL( blob );

    print(objectURL)

    img = window.Image.new()
    img.src = objectURL
    document.body.appendChild(img)

    wasm_exports.free_memory(array_ptr)
    wasm_exports.free_memory(res)

    display("cleaned up")

    # here to download the image

    # link = document.createElement( 'a' );
    # link.style.display = 'none';
    # document.body.appendChild( link );
    # link.href = objectURL;
    # link.download = 'data.png';
    # link.click();


# https://developer.mozilla.org/en-US/docs/Web/API/File
def file_change(event):
    print(event.target.files.item(0))
    file = event.target.files.item(0)
    if file is None:
        return

    display(f"name: {file.name}")
    display(f"size: {file.size}")
    display(f"type: {file.type}")
    display(f"lastModified: {file.lastModified}")

    promise = file.arrayBuffer()
    promise.then(lambda buffer: deal_a_buffer(buffer))

def hello():
    print("hello world")

    array = [1.0, 2.0, 3.0, 4.0, 5.0]

    array_ptr = wasm_exports.alloc_memory(len(array) * 8)
    display(f"array_ptr: {array_ptr}")
    array_view = Int32Array.new(wasm_exports.memory.buffer, array_ptr)
    array_view.set(array)

    deal = wasm_exports.deal_array(array_ptr, len(array))
    display(f"deal: {deal}")
    wasm_exports.free_memory(array_ptr)

hello()

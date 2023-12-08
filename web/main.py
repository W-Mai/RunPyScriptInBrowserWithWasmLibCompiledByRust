import sys
import ctypes
from pyscript import display, window, document
from js import wasm_exports, Array, Uint8Array, Int32Array, Uint32Array, Blob, URL

display(sys.version)

global_config = {
    "option": "option1",

    "images": [],
}


def get_buff(ptr):
    arr = Uint32Array.new(wasm_exports.memory.buffer, ptr)
    return (arr[0], arr[1])


# https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/ArrayBuffer
def deal_a_buffer(buf, index):
    buf_len = buf.byteLength
    array_ptr = wasm_exports.alloc_memory(buf_len)
    array_view = Uint8Array.new(wasm_exports.memory.buffer, array_ptr)
    array_view.set(Uint8Array.new(buf))

    global_config["images"][index] = {
        "array_ptr": array_ptr,
        "buf_len": buf_len
    }


# https://developer.mozilla.org/en-US/docs/Web/API/File
def file_change(event):
    files = event.target.files
    print(files.item(0))
    display(f"Uploaded {files.length} files")
    if files.length == 0:
        return

    global_config["images"] = [None] * files.length

    for i in range(files.length):
        file = files.item(i)
        display(f"name: {file.name} size: {file.size} type: {file.type} lastModified: {file.lastModified}")

        def tmp_deal_a_buffer(index):
            promise = file.arrayBuffer()
            promise.then(lambda buffer: deal_a_buffer(buffer, index))

        tmp_deal_a_buffer(i)


def deal_image(img):
    array_ptr = img["array_ptr"]
    buf_len = img["buf_len"]

    if array_ptr == 0 or buf_len == 0:
        display("no image")
        return

    res = wasm_exports.deal_image(array_ptr, buf_len)
    (img_buff, img_len) = get_buff(res)
    display(f"array_ptr: {array_ptr} buf_len: {buf_len} deal: {res} img_buff: {img_buff} img_len: {img_len}")
    img_view = Uint8Array.new(wasm_exports.memory.buffer, img_buff, img_len)

    blob = Blob.new([img_view])
    object_url = URL.createObjectURL(blob)

    print(object_url)

    img = window.Image.new()
    img.src = object_url
    img.style.width = "200px"
    document.body.appendChild(img)

    wasm_exports.free_memory(array_ptr)
    wasm_exports.free_memory(res)

    print(f"cleaned up: array_ptr {array_ptr} buf_len: {buf_len}")

    # here to download the image

    # link = document.createElement( 'a' );
    # link.style.display = 'none';
    # document.body.appendChild( link );
    # link.href = objectURL;
    # link.download = 'data.png';
    # link.click();


def button_click(event):
    select = document.getElementById("my-select")
    global_config["option"] = select.value
    display(f"Deal image with option: {global_config['option']}")

    for img in global_config["images"]:
        deal_image(img)


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

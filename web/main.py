import sys
import ctypes
from pyscript import display, window, document
from js import wasm_exports, Array, Uint8Array, Int32Array, Uint32Array, Blob, URL

display(sys.version)

global_config = {
    "option": "option1",

    "images": [],
}


class WasmImage(object):
    @staticmethod
    def from_buffer(buf):
        buf_len = buf.byteLength
        array_ptr = wasm_exports.alloc_memory(buf_len)
        array_view = Uint8Array.new(wasm_exports.memory.buffer, array_ptr)
        array_view.set(Uint8Array.new(buf))

        wasm_img = WasmImage(array_ptr, buf_len)
        wasm_img.img_view = array_view

        return wasm_img

    @staticmethod
    def from_wasm(array_ptr, buf_len):
        wasm_img = WasmImage(array_ptr, buf_len)
        wasm_img.img_view = Uint8Array.new(wasm_exports.memory.buffer, array_ptr, buf_len)

        return wasm_img

    # https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/ArrayBuffer
    @staticmethod
    def from_wasm_buffer(ptr):
        arr = Uint32Array.new(wasm_exports.memory.buffer, ptr)
        return WasmImage.from_wasm(arr[0], arr[1])

    def get_blob_url(self):
        blob = Blob.new([self.img_view])
        object_url = URL.createObjectURL(blob)
        return object_url

    def __init__(self, array_ptr, buf_len):
        self.array_ptr = array_ptr
        self.buf_len = buf_len
        self.img_view = None

    def __del__(self):
        wasm_exports.free_memory(self.array_ptr)
        print(f"cleaned up: array_ptr {self.array_ptr} buf_len: {self.buf_len}")


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

        def deal_a_buffer(buf, index):
            global_config["images"][index] = WasmImage.from_buffer(buf)
            return global_config["images"][index]

        def tmp_deal_a_buffer(index):
            promise = file.arrayBuffer()
            promise.then(lambda buffer: deal_a_buffer(buffer, index))

        tmp_deal_a_buffer(i)


def deal_image(img: WasmImage):
    array_ptr = img.array_ptr
    buf_len = img.buf_len

    if array_ptr == 0 or buf_len == 0:
        display("no image")
        return

    deal_res = wasm_exports.deal_image(array_ptr, buf_len)
    wasm_img = WasmImage.from_wasm_buffer(deal_res)
    # display(f"array_ptr: {array_ptr} buf_len: {buf_len} "
    #         f"deal: {deal_res} img_buff: {wasm_img.array_ptr} img_len: {wasm_img.buf_len}")

    object_url = wasm_img.get_blob_url()
    print(object_url)

    img_comp = window.Image.new()
    img_comp.src = object_url
    img_comp.style.width = "200px"

    # here to download the image
    link = document.createElement('a')
    link.textContent = 'download'
    link.href = object_url
    link.download = 'data.png'

    info = document.createElement("label")
    info.textContent = (f"array_ptr: {array_ptr} buf_len: {buf_len}"
                        f"deal: {deal_res} img_buff: {wasm_img.array_ptr} img_len: {wasm_img.buf_len}")
    info.style.fontSize = "12px"
    info.style.width = "200px"

    small_group = document.createElement("div")
    small_group.style.display = "flex"
    small_group.style.flexDirection = "column"
    small_group.style.alignItems = "center"
    small_group.style.margin = "10px"
    small_group.appendChild(img_comp)
    small_group.appendChild(link)
    small_group.appendChild(info)

    del img
    del wasm_img

    return small_group


def button_click(event):
    select = document.getElementById("my-select")
    global_config["option"] = select.value
    display(f"Deal image with option: {global_config['option']}")

    big_group = document.createElement("div")
    big_group.style.display = "flex"
    big_group.style.flexDirection = "row"
    big_group.style.flexWrap = "wrap"
    big_group.style.alignItems = "center"

    document.body.appendChild(big_group)

    for img in global_config["images"]:
        small_group = deal_image(img)
        big_group.appendChild(small_group)


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

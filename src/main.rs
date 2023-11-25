#![no_main]

#[no_mangle]
fn fab(n: i32) -> i32 {
    if n <= 2 {
        return 1;
    }
    let mut count = 0;
    let mut a = 1;
    let mut b = 1;
    let mut c: i32;

    while count <= n - 2 {
        c = a + b;
        a = b;
        b = c;

        count += 1;
    }

    a
}

#[no_mangle]
fn fake_img() -> usize {
    // Image loading/saving is outside scope of this library
    let width = 10;
    let height = 10;
    let fakebitmap = vec![imagequant::RGBA { r: 100, g: 200, b: 250, a: 255 }; width * height];

    // Configure the library
    let mut liq = imagequant::new();
    liq.set_speed(5).unwrap();
    liq.set_quality(70, 99).unwrap();

    // Describe the bitmap
    let mut img = liq.new_image(&fakebitmap[..], width, height, 0.0).unwrap();

    // The magic happens in quantize()
    let mut res = match liq.quantize(&mut img) {
        Ok(res) => res,
        Err(err) => panic!("Quantization failed, because: {err:?}"),
    };

    // Enable dithering for subsequent remappings
    res.set_dithering_level(1.0).unwrap();

    // You can reuse the result to generate several images with the same palette
    let (palette, pixels) = res.remapped(&mut img).unwrap();

    println!("Done! Got palette {palette:?} and {} pixels with {}% quality", pixels.len(), res.quantization_quality().unwrap());
    pixels.len()
}

#[no_mangle]
fn deal_array(data: *const i32, length: usize) -> usize {
    let slice = unsafe { std::slice::from_raw_parts(data, length) };
    let mut sum = 0;
    for i in slice {
        sum += i;
    }
    return sum as usize;
}

#[no_mangle]
fn alloc_memory(size: usize) -> u32 {
    let mut v: Vec<u8> = Vec::with_capacity(size);
    let ptr = v.as_mut_ptr();
    std::mem::forget(v);
    return ptr as u32;
}

#[no_mangle]
fn free_memory(ptr: u32, size: usize) {
    unsafe {
        let _v = Vec::from_raw_parts(ptr as *mut u8, size, size);
    }
}

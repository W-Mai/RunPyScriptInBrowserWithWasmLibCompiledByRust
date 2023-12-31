#![no_main]

use png::ColorType;

#[allow(dead_code)]
struct Buffer {
    ptr: u32,
    size: usize,
}

#[no_mangle]
fn deal_image(data: *const u8, length: usize) -> u32 {
    let slice = unsafe { std::slice::from_raw_parts(data, length) };
    let mut image = png::Decoder::new(slice).read_info().unwrap();
    let buffer_size = image.output_buffer_size();
    let mut img_data = vec![0; buffer_size];
    let image_info = image.next_frame(&mut img_data).unwrap();

    let width = image_info.width as usize;
    let height = image_info.height as usize;

    // Configure the library
    let mut liq = imagequant::new();
    liq.set_speed(5).unwrap();
    liq.set_quality(70, 99).unwrap();

    let color_type = image_info.color_type;
    // I only support RGBA and RGB now
    let rgba = match color_type {
        ColorType::Rgb => {
            img_data
                .chunks_exact_mut(3)
                .map(|chunk| imagequant::RGBA {
                    r: chunk[0],
                    g: chunk[1],
                    b: chunk[2],
                    a: 0xFF,
                })
                .collect::<Vec<_>>()
        }
        ColorType::Rgba => {
            img_data
                .chunks_exact_mut(4)
                .map(|chunk| imagequant::RGBA {
                    r: chunk[0],
                    g: chunk[1],
                    b: chunk[2],
                    a: chunk[3],
                })
                .collect::<Vec<_>>()
        }
        ColorType::Grayscale => { panic!("Grayscale is not supported yet.") }
        ColorType::Indexed => { panic!("Indexed is not supported yet.") }
        ColorType::GrayscaleAlpha => { panic!("GrayscaleAlpha is not supported yet.") }
    };

    // Describe the bitmap
    let mut img = liq.new_image(rgba, width, height, 0.0).unwrap();

    // The magic happens in quantize()
    let mut res = match liq.quantize(&mut img) {
        Ok(res) => res,
        Err(err) => panic!("Quantization failed, because: {err:?}"),
    };

    // Enable dithering for subsequent remappings
    res.set_dithering_level(1.0).unwrap();

    // You can reuse the result to generate several images with the same palette
    let (palette, pixels) = res.remapped(&mut img).unwrap();

    // write to png file in memory
    let mut png_data = Vec::new();
    {
        let mut encoder = png::Encoder::new(&mut png_data, width as u32, height as u32);
        encoder.set_color(ColorType::Indexed);
        encoder.set_depth(png::BitDepth::Eight);

        // convert palette to u8
        let palette = palette
            .iter()
            .map(|rgba| [rgba.r, rgba.g, rgba.b])
            .flatten()
            .collect::<Vec<_>>();

        encoder.set_palette(palette.as_slice());
        let mut writer = encoder.write_header().unwrap();
        writer.write_image_data(&pixels).unwrap();
    }

    let buffer = png_data.leak();
    let ptr = buffer.as_ptr();

    Box::into_raw(Box::new(Buffer {
        ptr: ptr as u32,
        size: buffer.len(),
    })) as u32
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

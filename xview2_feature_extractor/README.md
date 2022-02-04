
# DisaVu XView2 Feature Extractor

The XView2 Feature Extractor is a custom-built solution to extract the required features from the XView2 Data Set. Essentially, the program takes labels (polygon data) and satellite images as input and then extracts and preprocesses image data for each label (polygon) and stores the results in output images. Those output images are then subsequently for training the machine learning part of the DisaVu system.

*Check the main README.md of this repository for further details.*


## Installing Dependencies

To build this project, you will have to have Rust installed. The easiest way to get started is by following the instructions on https://rustup.rs.


## Development

In order to get started with development, run:
```bash
cargo run -- \
          --labels-dir xview_2_dataset/labels \
          --images-dir xview_2_dataset/images \
          --output-dir xview_2_dataset/output \
          --output-size 256 \
          --labels-prefix hurricane
```

This will download, install, and build all required dependencies automatically. Once built, the tool will be started with debug information. Note that you are required to specify the XView2 labels directory, the XView2 images directory, an output directory, an ouput image size, and a prefix used for the output files.


## Building

To build for production/deployment, run:

```bash
cargo build --release -- \
            --labels-dir xview_2_dataset/labels \
            --images-dir xview_2_dataset/images \
            --output-dir xview_2_dataset/output \
            --output-size 256 \
            --labels-prefix hurricane
```

Alternatively, to directly start a production build, run:

```bash
cargo run --release -- \
          --labels-dir xview_2_dataset/labels \
          --images-dir xview_2_dataset/images \
          --output-dir xview_2_dataset/output \
          --output-size 256 \
          --labels-prefix hurricane
```

This will download, install, and build all required dependencies automatically. Once built, the tool will be started with debug information. Note that you are required to specify the XView2 labels directory, the XView2 images directory, an output directory, an ouput image size, and a prefix used for the output files.


## Available Command Line Options

```
Usage: xview2_feature_extractor --labels-dir <labels-dir> --images-dir <images-dir> --output-dir <output-dir> [--labels-prefix <labels-prefix>] [--output-size <output-size>]

XView2 Feature Extractor.

Options:
  --labels-dir      the labels directory of the XView2 training data.
  --images-dir      the images directory of the XView2 training data.
  --output-dir      the output directory where the images should be saved.
  --labels-prefix   only load label files that start with the specified value.
  --output-size     the size of the output image.
  --help            display usage information
```

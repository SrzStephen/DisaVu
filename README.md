# BuildingDamage

###Xview2FeatureExtractor
install rustup
```
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```
restart your shell

Build the rust executable
```
cargo build --release
```

Run the code
```
time RUST_LOG=DEBUG cargo run --release -- --labels-dir xview_2_dataset/labels --images-dir xview_2_dataset/images --output-dir xview_2_dataset/output --output-size 256 --labels-prefix hurricane
```




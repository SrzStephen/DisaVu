
# DisaVu GeoServ

GeoServ is a custom-built solution to serve GeoJSON and heatmap data for use in DisaVu.

*Check the main README.md of this repository for further details.*



## Installing Dependencies

To build this project, you will have to have Rust installed. The easiest way to get started is by following the instructions on https://rustup.rs.


## Development

In order to get started with development, simply run the following command:
```bash
cargo run -- --data-dir your_data_directory
```

This will download, install, and build all required dependencies automatically. Once built, development server will be started on http://127.0.0.1:8088/. Note that you are required to specify a directory which contains the data described below.


## Building

To build for production/deployment, run:

```bash
cargo build --release
```

Alternatively, to directly start a production build, run:

```bash
cargo build --release -- --data-dir your_data_directory.
```

Note that you are required to specify a directory which contains the data described below.


## Available Command Line Options

```
Usage: geoserv [--hostname <hostname>] [--port <port>] --data-dir <data-dir> [--workers <workers>]

GeoServ.

Options:
  --hostname        the hostname on which the server will start listening.
  --port            the images directory of the XView2 training data.
  --data-dir        the directory where the GeoJSON files are located.
  --workers         the number of worker threads to use.
  --help            display usage information
```

# Data Directory Structure

To use the server, you need to specify a directory that itself contains a number of directories, one for each disaster zone you wish to host. Within those individual per disaster-zone directories you will need to place the GeoJSON files that should be made available to the front-end. The type of the GeoJSON definitions determines how they are presented. Amenities need to be specified as a `FeatureCollection` of `Point` structures, whereas the structure polygons need to be specified as a `FeatureCollection` of `Polygon` structures.

Consider the following directory structure as an example:

```
test_data/
├── houston
│   ├── amenities.geojson
│   ├── structures-affected.geojson
│   └── structures-unaffected.geojson
└── vegas
    ├── amenities.geojson
    ├── structures-affected.geojson
    └── structures-unaffected.geojson
```

Given this structure with valid GeoJSON files, the following endpoints will be made available automatically:

```
https://disavu.silentbyte.com/geoserv/geo/houston/amenities
https://disavu.silentbyte.com/geoserv/geo/houston/structures-affected
https://disavu.silentbyte.com/geoserv/geo/houston/structures-affected/heatmap
https://disavu.silentbyte.com/geoserv/geo/houston/structures-unaffected
https://disavu.silentbyte.com/geoserv/geo/houston/structures-unaffected/heatmap

https://disavu.silentbyte.com/geoserv/geo/vegas/amenities
https://disavu.silentbyte.com/geoserv/geo/vegas/structures-affected
https://disavu.silentbyte.com/geoserv/geo/vegas/structures-affected/heatmap
https://disavu.silentbyte.com/geoserv/geo/vegas/structures-unaffected
https://disavu.silentbyte.com/geoserv/geo/vegas/structures-unaffected/heatmap
```

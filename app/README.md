
# DisaVu

*Check the main README.md of this repository for further details.*


## Installing Dependencies

Install [Yarn](https://yarnpkg.com/getting-started/migration) by running:

```bash
npm install -g yarn
```

Once Yarn is set up correctly, install the project dependencies:

```bash
yarn install
```


## Development

To start a development server on http://127.0.0.1:8080, simply run:

```bash
yarn serve
```


## Building

To build for production/deployment, run:

```bash
yarn build
```

After the command completed successfully, you can find the production build in the `./dist` folder. Note that the folder contains a file called `disaster-zones.json`. This file lists all the zones that should be listed on the website. You may want to edit this file and adjust its content to match the files available on the server.

The JSON file must be an array of objects following this structure:

```json
[
    {
        "id": "d6be9a72-99d6-4c56-bd7f-f1dba4ba413a",
        "name": "Las Vegas",
        "center": {
            "lat": 36.1909007,
            "lng": -115.1270185,
            "zoom": 10
        },
        "beforeLayer": {
            "urlTemplate": "https://disavu.silentbyte.com/tiles/rgb/before/{z}/{x}/{y}.png?r=1&r_range=[0,255]&g=2&g_range=[0,255]&b=3&b_range=[0,255]",
            "attributionHtml": "&copy; <a href=\\\"https://www.maxar.com/open-data\\\">Maxar</a>"
        },
        "afterLayer": {
            "urlTemplate": "https://disavu.silentbyte.com/tiles/rgb/after/{z}/{x}/{y}.png?r=1&r_range=[0,255]&g=2&g_range=[0,255]&b=3&b_range=[0,255]",
            "attributionHtml": "&copy; <a href=\\\"https://www.maxar.com/open-data\\\">Maxar</a>"
        },
        "amenitiesUrl": "https://disavu.silentbyte.com/geoserv/geo/vegas/amenities",
        "affectedStructuresUrl": "https://disavu.silentbyte.com/geoserv/geo/vegas/structures-affected",
        "unaffectedStructuresUrl": "https://disavu.silentbyte.com/geoserv/geo/vegas/structures-unaffected",
        "heatmapUrl": "https://disavu.silentbyte.com/geoserv/geo/vegas/structures-affected/heatmap"
    }
]
```

| Field                   | Description                                                                                                                                                       |
|-------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| id                      | A UUID that uniquely identifies the disaster zone.                                                                                                                |
| name                    | The name of the disaster.                                                                                                                                         |
| center                  | An object specifying the center of the disaster zone and the default zoom level.                                                                                  |
| beforeLayer             | An object specifying a Leaflet URL template and attribution for pointing to a tile server that provides satellite images from before the disaster. May be `null`. |
| afterLayer              | An object specifying a Leaflet URL template and attribution for pointing to a tile server that provides satellite images from before the disaster. May be `null`. |
| amenitiesUrl            | The URL where the amenities can be found. May be `null`.                                                                                                          |
| affectedStructuresUrl   | The URL where the polygons for the affected structures can be found. May be `null`.                                                                               |
| unaffectedStructuresUrl | The URL where the polygons for the unaffected structures can be found. May be `null`.                                                                             |
| heatmapUrl              | The URL where the heatmap for the disaster can be found. May be `null`.                                                                                           |



## Terracotta

If you know what a python virtual envrionment is, use it to install terracotta.

If you don't, then don't worry and just install it as you normally would.
```bash
sudo apt install python3-pip -y
pip3 install terracotta
```

On a beefy server (because this process is very memory intensive) run the stage_3 in data_gen. It will generate a GeoTIFF split into bands in a folder called ```processing```.
Once this is done:

Optimise your raster with
```
preproccess_combined terracotta optimize-rasters geotifs_intermediate/*.tif -o optimized/ --reproject
terracotta ingest optimized/{name}_band{band}.tif -o a.sqlite
```
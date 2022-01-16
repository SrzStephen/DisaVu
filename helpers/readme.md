# Helpers in here
To be converted to something better later

##Tif2band:
Terracotta tileserver will only automatically process the first band in a geotif, and treat it as greyscale.

The fix for this is to pull out each band (R G B) which then lets you set up things properly

## Inference_split_tif
To make your life a lot easier you should probably make sure that your tifs refer to the same region of lat/lons,
regardless of the zoom factor.

This splits two tif files into the corresponding intersection geotif.

## Preprocess Train

For model 1 we need to take the known boundaries from the json file and convert them into a mask.

The mask is encoded so that 0 = blank, 1 = footprint 2 = contact 3 = boundary


## Post_process

The masks that get produced by the second model need to be converted into something more useful.
This model converts the mask to a polygon, then converts that polygon from pixel space to WGS84.
```geojson

  "type":"FeatureCollection",
  "features":
  [
    {"type":"Feature",
    "geometry":{
    "type":"Polygon",
    "coordinates":[[[-96.588742,46.260198],[-96.588742,46.260309],[-96.588854,46.260309],[-96.588854,46.260198],
    [-96.588742,46.260198]]]},"properties":{"release":1,"capture_dates_range":""}},
    }
   ]

```

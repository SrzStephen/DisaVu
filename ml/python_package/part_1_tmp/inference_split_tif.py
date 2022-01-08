from solaris.tile.raster_tile import RasterTiler
import gdal
from gdalconst import GA_ReadOnly
from typing_extensions import TypedDict
from shapely.geometry import box
import matplotlib.pyplot as plt


# from osgeo import gdal
#
# bbox = (xmin,ymin,xmax,ymax)
#
# gdal.Translate('output_crop_raster.tif', 'input_raster.tif', projWin = bbox)

class BoundsDict(TypedDict):
    minx: str
    maxx: str
    miny: str
    maxy: str


class GeoData():
    def __init__(self, filename: str):
        data = gdal.Open(filename, GA_ReadOnly)
        geoTransform = data.GetGeoTransform()
        minx = geoTransform[0]
        maxy = geoTransform[3]
        maxx = minx + geoTransform[1] * data.RasterXSize
        miny = maxy + geoTransform[5] * data.RasterYSize
        self.bounds: BoundsDict = BoundsDict(minx=minx, maxx=maxx, miny=miny, maxy=maxy)

    def __repr__(self):
        return self.bounds.__str__()


if __name__ == "__main__":
    # Files
    before = '/home/stephen/Downloads/10500100271BF800_before.tif'
    after = '/home/stephen/Downloads/1050010027849000_after.tif'

    # Get intersection area
    a = box(**GeoData(before).bounds).intersection(
        box(**GeoData(after).bounds)
    )
    x, y = a.exterior.xy
    # print(x, y)
    # plt.plot(x, y)
    # plt.show()

    # From here, do one of the files
    raster_common_param = dict(dest_tile_size=(500, 500),
                               verbose=False,
                               force_load_cog=True,
                               aoi_boundary=a)

    tiler = RasterTiler(dest_dir="before", **raster_common_param)
    tiler.tile(before)

    # use the bounds from the previous cycle
    tiler = RasterTiler(dest_dir="after", tile_bounds=tiler.tile_bounds, **raster_common_param)
    raster_bounds_crs = tiler.tile(after)
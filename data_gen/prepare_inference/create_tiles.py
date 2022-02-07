from solaris.tile.raster_tile import RasterTiler
import gdal
from gdalconst import GA_ReadOnly
from typing_extensions import TypedDict
from shapely.geometry import box
import matplotlib.pyplot as plt
from pathlib import Path
from terracotta.scripts.optimize_rasters import optimize_rasters
from terracotta.scripts.ingest import ingest
from terracotta import get_driver
import rasterio
import sqlite3
from typing import List
from click.testing import CliRunner


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


def split_files_by_bounding_box(before: Path, after: Path, dump_base: Path):
    b_str = before.__str__()
    a_string = after.__str__()
    if not dump_base.exists():
        dump_base.mkdir(parents=True)

    # Get intersection area
    a = box(**GeoData(b_str).bounds).intersection(
        box(**GeoData(a_string).bounds)
    )

    # From here, do one of the files
    raster_common_param = dict(dest_tile_size=(360, 360),
                               verbose=False,
                               force_load_cog=True,
                               aoi_boundary=a)

    tiler = RasterTiler(dest_dir=dump_base / "before", **raster_common_param)
    tiler.tile(before.__str__())

    # use the bounds from the previous cycle
    tiler2 = RasterTiler(dest_dir=dump_base / "after", tile_bounds=tiler.tile_bounds, **raster_common_param)
    tiler2.tile(after.__str__())

if __name__ == "__main__":
    # Files
    before = '/home/stephen/Downloads/10500100271BF800.tif'
    after = '/home/stephen/Downloads/1050010027849000.tif'
    dump_b = Path().resolve()
    # generate tiles
    split_files_by_bounding_box(Path(before), Path(after), dump_base=dump_b)
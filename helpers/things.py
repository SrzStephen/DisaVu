import click
from solaris.tile.raster_tile import RasterTiler
import gdal
from gdalconst import GA_ReadOnly
from typing_extensions import TypedDict
from shapely.geometry import box
from pathlib import Path

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


@click.command()
@click.option('--input_tif_1', type=click.Path(exists=True))
@click.option('--input_tif_2', type=click.Path(exists=True))
@click.option('--tilesize_pix', type=click.INT, default=500)
def cli(input_tif_1: str, input_tif_2: str, tilesize_pix: int):
    a = box(**GeoData(input_tif_1).bounds).intersection(
        box(**GeoData(input_tif_2).bounds)
    )
    raster_common_param = dict(dest_tile_size=(tilesize_pix, tilesize_pix),
                               verbose=False,
                               force_load_cog=True,
                               aoi_boundary=a)
    run_once = False
    for tif_img in [input_tif_1, input_tif_2]:
        new_file_name = Path(tif_img).stem + "trimmed.tif"
        if not run_once:
            tiler = RasterTiler(dest_dir=new_file_name, **raster_common_param)
            tiler.tile(new_file_name)
        else:
            tiler2 = RasterTiler(dest_dir="after", tile_bounds=tiler.tile_bounds, **raster_common_param)
            # use the bounds from the previous cycle
            tiler2.tile(new_file_name)

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


def split_files_by_bounding_box(before: Path, after: Path):
    intersecting_box = box(**GeoData(before.__str__()).bounds).intersection(
        box(**GeoData(after.__str__()).bounds))

    raster_common_param = dict(dest_tile_size=(500, 500),
                               verbose=False,
                               force_load_cog=True,
                               aoi_boundary=intersecting_box)
    tiler = RasterTiler(dest_dir="processed", **raster_common_param)
    tiler.tile(before.__str__())

    # use the bounds from the previous cycle
    tiler2 = RasterTiler(dest_dir="processed", tile_bounds=tiler.tile_bounds, **raster_common_param)
    tiler2.tile(after.__str__())


def split_geotiff_to_components(path_to_search: Path):
    # Generate all the paths before writing additional tifs.
    # Needed to split bands out
    for file in [x for x in path_to_search.glob('*tif')]:
        with rasterio.open(file) as src:
            profile = src.profile.copy()
            profile['photometric'] = "RGB"
            img = src.read()
            profile['count'] = 1
            for i in range(img.shape[0]):
                out_file = path_to_search / file.stem / f"_band{i + 1}.tif"
                with rasterio.open(out_file, 'w', **profile) as dst:
                    dst.write(img[i], 1)


def do_tilesover_ops(path_to_search: Path) -> Path:
    """:returns location of sqllite db"""
    out_dir = path_to_search.parent / "output"
    sqllitedb = out_dir.parent / "database.sqlite"
    if not out_dir.exists():
        out_dir.mkdir()
    optimize_rasters(output_folder=out_dir, reproject=True, raster_files=[x for x in path_to_search.glob('*.tif')])
    ingest(raster_patern=out_dir / "{name}_band{band}.tif", output_file=sqllitedb)
    return sqllitedb


def modify_dataset(path_to_db: Path, new_path: str):
    con = sqlite3.connect(path_to_db, timeout=10)
    cur = con.cursor()
    cur2 = con.cursor()
    # Sqllite doesn't have split string so this is dumb but eeh.
    for row in cur.execute("Select filepath from datasets"):
        file_to_change = Path(row[0]).name()
        path_change_val = str(Path(new_path) / file_to_change)
        cur2.execute(f"update datasets set filepath={path_change_val} where filepath={path_change_val}")


if __name__ == "__main__":
    # Files
    modify_dataset("/home/stephen/Documents/terracotta/a.sqlite", "Aaa")
    before = '/home/stephen/Downloads/10500100271BF800_before.tif'
    after = '/home/stephen/Downloads/1050010027849000_after.tif'
    split_files_by_bounding_box(before, after)
    split_geotiff_to_components(Path().resolve() / "processed")
    sqllite_db = do_tilesover_ops(Path().resolve() / "output")
    modify_dataset(sqllite_db, "/files/")

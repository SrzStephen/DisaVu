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


def split_geotiff_to_components(tifs: List[Path], path_to_dump: Path):
    # Generate all the paths before writing additional tifs.
    # Needed to split bands out
    print(f"Generating your geotifs split by band in {path_to_dump}")
    if not path_to_dump.exists():
        path_to_dump.mkdir(parents=True)
    for file in tifs:
        with rasterio.open(file) as src:
            profile = src.profile.copy()
            profile['photometric'] = "RGB"
            img = src.read()
            profile['count'] = 1
            for i in range(img.shape[0]):
                out_file = path_to_dump / f"{file.stem}_band{i + 1}.tif"
                with rasterio.open(out_file, 'w', **profile) as dst:
                    dst.write(img[i], 1)

def do_tilesover_ops(in_dir: Path, out_dir: Path) -> Path:
    """:returns location of sqllite db"""
    # Ok so this is kind of strange, and I've never seen it before
    # The underlying function here doesn't seem to be playing nice becuase of somethign click related..
    # I dont understand why, so instead I'm going to cheat and run it via clirunner.
    runner = CliRunner()
    print("Optimising your rasters, this may take a while")
    runner.invoke(optimize_rasters,
                  args=['--output-folder', out_dir.__str__(), '--reproject','--nproc',8,
                        '--overwrite', (in_dir / "*.tif").__str__()])

if __name__ == "__main__":
    base_path = Path().resolve()
    path_in = base_path / "geotifs_in"
    path_optimised = base_path /"geotifs_intermediate"
    path_processed = base_path /"geotifs_out"

    if not path_in.exists():
        raise ValueError("Please create a folder called geotifs_in and throw the tifs that you want terracotta to serve in there")
    else:
        geotiff_list = [x for x in path_in.glob("*.tif")]
        if len(geotiff_list) == 0:
            raise ValueError(f"no geotifs found in {path_in}")

    if not path_optimised.exists():
        path_optimised.mkdir()
    if not path_processed.exists():
        path_processed.mkdir()
    split_geotiff_to_components(geotiff_list,path_optimised)
    do_tilesover_ops(path_optimised,path_processed)




import rasterio
from pathlib import Path
import click

@click.command()
@click.option('--path_to_search', type=click.Path(exists=True))
def cli(path_to_search:str):
    # Generate all the paths before writing additional tifs.
    # Needed to split bands out
    for file in [x for x in Path(path_to_search).glob('*tif')]:
        with rasterio.open(file) as src:
            profile = src.profile.copy()
            profile['photometric'] = "RGB"
            img = src.read()
            profile['count'] = 1
            for i in range(img.shape[0]):
                OUT_RASTER = path_to_search + file.stem + "_band{}.tif"
                out_file = OUT_RASTER.format(i + 1)
                with rasterio.open(out_file, 'w', **profile) as dst:
                    dst.write(img[i], 1)


if __name__ == "__main__":
    cli()
from osgeo import gdal
import solaris as sol
import matplotlib.pyplot as plt
import numpy as np
from pandas import DataFrame
from typing import Union
import click
from pathlib import Path
from tqdm import tqdm
from osgeo import gdal_array
import matplotlib
import pandas as pd
from sklearn.model_selection import train_test_split
from PIL import Image
import albumentations as A
from solaris.vector.mask import footprint_mask, boundary_mask, contact_mask
from PIL import Image

# modification of the existing function because I wanted a nicer output to work with
def mod_df_to_px_mask(df, channels=['footprint'], out_file=None, reference_im=None,
                      geom_col='geometry', do_transform=None, affine_obj=None,
                      shape=(900, 900), out_type='int', burn_value=1, **kwargs):
    if isinstance(channels, str):  # e.g. if "contact", not ["contact"]
        channels = [channels]

    mask_dict = {}
    if 'footprint' in channels:
        mask_dict['footprint'] = footprint_mask(
            df=df, reference_im=reference_im, geom_col=geom_col,
            do_transform=do_transform, affine_obj=affine_obj, shape=shape,
            out_type=out_type, burn_value=burn_value
        )
    if 'boundary' in channels:
        mask_dict['boundary'] = boundary_mask(
            footprint_msk=mask_dict.get('footprint', None),
            reference_im=reference_im, geom_col=geom_col,
            boundary_width=kwargs.get('boundary_width', 3),
            boundary_type=kwargs.get('boundary_type', 'inner'),
            burn_value=burn_value, df=df, affine_obj=affine_obj,
            shape=shape, out_type=out_type
        )
    if 'contact' in channels:
        mask_dict['contact'] = contact_mask(
            df=df, reference_im=reference_im, geom_col=geom_col,
            affine_obj=affine_obj, shape=shape, out_type=out_type,
            contact_spacing=kwargs.get('contact_spacing', 10),
            burn_value=burn_value,
            meters=kwargs.get('meters', False)
        )

    return mask_dict


def transform_file_to_8_bit(src_file: str, dst_file: str) -> None:
    translate_options = gdal.TranslateOptions(format='JPEG',
                                              outputType=gdal.GDT_Byte,
                                              scaleParams=[''],
                                              )
    gdal.Translate(destName=dst_file,
                   srcDS=src_file, options=translate_options)


def generate_mask_for_image(src_geo: Union[str, Path], src_tif: str, dst_file: str) -> bool:
    # mask needs to be a combo of bounds and box
    try:
        src_geo: Union[DataFrame, str]  # It's not a dataframe but df is incorrectly typed and it annoys me
        # fbc_mask = sol.vector.mask.df_to_px_mask(df=src_geo,
        #                                          channels=['footprint','contact', 'boundary'],
        #                                          reference_im=src_tif,
        #                                          boundary_width=5, contact_spacing=10, meters=True,
        #                                          shape=(650,650)
        #                                             )
        fbc_mask = mod_df_to_px_mask(df=src_geo,
                                     channels=['footprint', 'contact', 'boundary'],
                                     reference_im=src_tif,
                                     boundary_width=5, contact_spacing=10, meters=True,
                                     shape=(650, 650)
                                     )

        # squashing it down, currently R = Footprint, B= contact, G= bounary,
        # squash it so 0 = blank, 1 = footprint 2 = contact 3 = boundary
        mask_form = fbc_mask['boundary']
        mask_form = np.where(mask_form == 0, fbc_mask['contact'] * 2, mask_form)
        mask_form = np.where(mask_form == 0, fbc_mask['footprint']* 3, mask_form)
        Image.fromarray(mask_form).save(dst_file)
        #matplotlib.image.imsave(dst_file, mask_form)
        return True
    except ValueError:
        return False


def remove_prefix(str, prefix):
    if str.startswith(prefix):
        return str[len(prefix):]
    else:
        return str


@click.command()
@click.option('--input_tif', type=click.Path(exists=True))
@click.option('--input_geodata', type=click.Path(exists=True))
@click.option('--output_folder', type=click.Path(exists=False))
@click.option('--image_type', type=click.STRING, default='RGB-PanSharpen')
@click.option('--train_fraction', type=click.FLOAT, default=0.8)
def cli(input_tif: str, input_geodata: str, output_folder: str, image_type: str, train_fraction: float):
    output_tif = Path(output_folder) / "img"
    output_mask = Path(output_folder) / "mask"
    output_csv = Path(output_folder) / "csv"

    df = pd.DataFrame(columns=['image', 'label'])
    for outdir in [output_tif, output_mask, output_csv]:
        if not outdir.exists():
            outdir.mkdir(parents=True)

    file_names = [x for x in Path(input_geodata).glob('*.geojson')]
    for file in tqdm(file_names):
        file: Path
        partial_filename = remove_prefix(file.stem, 'buildings_')
        tif_name = (Path(input_tif) / f"{image_type}_{partial_filename}.tif").__str__()
        if not Path(tif_name).exists():
            continue

        geojson_name = file.__str__()

        mask_worked = generate_mask_for_image(src_geo=geojson_name,
                                              src_tif=tif_name,
                                              dst_file=(output_mask / f"{partial_filename}.png").__str__())
        if mask_worked:
            transform_file_to_8_bit(src_file=tif_name,
                                    dst_file=(output_tif / f"{partial_filename}.jpg").__str__())
            df = df.append(
                dict(image=output_tif / f"{partial_filename}.jpg", label=output_mask / f"{partial_filename}.jpg"),
                ignore_index=True)

    train, test = train_test_split(df, train_size=train_fraction)
    train.to_csv(output_csv / "train.csv", index=False)
    test.to_csv(output_csv / "test.csv", index=False)


if __name__ == "__main__":
    cli()

import boto3
import shutil
from osgeo import gdal
import numpy as np
from pandas import DataFrame
from typing import Union
from pathlib import Path
from tqdm import tqdm
from solaris.vector.mask import footprint_mask, boundary_mask, contact_mask
from PIL import Image





urls = [
    "AOIs/AOI_2_Vegas/misc/AOI_2_Vegas_Train.tar.gz",
    "AOIs/AOI_3_Paris/misc/AOI_3_Paris_Train.tar.gz",
    "AOIs/AOI_4_Shanghai/misc/AOI_4_Shanghai_Train.tar.gz",
    "AOIs/AOI_5_Khartoum/misc/AOI_5_Khartoum_Train.tar.gz"
]


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
        mask_form = np.where(mask_form == 0, fbc_mask['footprint'] * 3, mask_form)
        Image.fromarray(mask_form).save(dst_file)
        return True
    except ValueError:
        return False


def remove_prefix(str, prefix):
    if str.startswith(prefix):
        return str[len(prefix):]
    else:
        return str


def download_data(url: str, download_path: Path) -> None:
    s3 = boto3.client('s3')
    if download_path.exists():

        return
    else:
        with open(download_path, 'wb') as fp:
            print(f"downloading {url} ths may take a while")
            s3.download_fileobj('spacenet-dataset', url, fp)


def unzip_data(file_gz: str, extract_path: Path):
    # unpack
    if not extract_path.exists():
        extract_path.mkdir()
    try:  # Annoyingly Gz isn't a full stream so need to extract everything then do stuff
        shutil.unpack_archive(filename=file_gz, extract_dir=extract_path, format='gztar')
    except shutil.ReadError:
        print(
            f"Failed to unzip {file_gz}, It's probably corrupt. I'd suggest deleting the copy you have and trying again, skipping")
        raise


def process_data(data_to_process: Path, process_folder: Path):
    # structure of this that we care about is
    # RGB-PANSharpen
    # Geojson
    print(f"Processing {data_to_process.name}")
    pan_dir = data_to_process / "RGB-PanSharpen"
    geo_dir = data_to_process / "geojson" / "buildings"
    mask_dir = process_folder / "mask"
    tif_dir = process_folder / "img"
    for proc_folder in [tif_dir, mask_dir]:
        if not proc_folder.exists():
            proc_folder.mkdir(parents=True)

    # I can pass length to TQDM to get it to play nice with a generator (Path.glob)
    # instead of this, but expansion is less effort
    for file in tqdm([x for x in geo_dir.glob("*geojson")]):
        partial_filename = remove_prefix(file.stem, 'buildings_')
        tif_name = (Path(pan_dir) / f"RGB-PanSharpen_{partial_filename}.tif").__str__()
        if not Path(tif_name).exists():
            continue
        geojson_name = file.__str__()
        mask_worked = generate_mask_for_image(src_geo=geojson_name,
                                              src_tif=tif_name,
                                              dst_file=(mask_dir / f"{partial_filename}.png").__str__())

        if mask_worked:
            transform_file_to_8_bit(src_file=tif_name,
                                    dst_file=(tif_dir / f"{partial_filename}.jpg").__str__())


def make_zip(processed_dir: Path, AOI_name: str):
    # Compresses data
    print(f"making zip {AOI_name}")
    shutil.make_archive(base_name=(processed_dir.parent / AOI_name).__str__(),
                        format='gztar',
                        root_dir=processed_dir / AOI_name
                        )


def upload_zip_to_s3(zip_file: Path, bucket_name: str, file_name: str) -> None:
    print(f"uploading {file_name}")
    s3 = boto3.client('s3')
    with open(zip_file, 'rb') as fp:
        s3.upload_fileobj(fp, bucket_name, file_name, ExtraArgs=dict(RequestPayer='requester',
                                                                     ACL='public-read'))


if __name__ == "__main__":
    data_folder = Path(__file__).parent / 'data'
    download_folder = data_folder / 'downloads'
    processed_folder = data_folder / 'processed'
    unzipped_folder = data_folder / 'unzipped'
    zip_folder = data_folder / 'zip_upload_s3'

    for url in tqdm(urls):
        for folder in [download_folder, processed_folder, unzipped_folder]:
            if not folder.exists():
                folder.mkdir(parents=True)
        tar_gz_name = url.split('/')[-1]
        tar_gz_stem = tar_gz_name.split(".")[0]  # Note Path.stem on a tar.gz will return foo.tar instead of foo
        download_path = download_folder / tar_gz_name
        download_data(url, download_path)

        try:
            # stem is name without the extension
            unzip_data(download_path, unzipped_folder)
            pass
        except shutil.ReadError:
            # If failed to open zip (eg partially dl'd file) then skip
            continue

        process_data(data_to_process=unzipped_folder / tar_gz_stem, process_folder=processed_folder / tar_gz_stem)
        make_zip(processed_dir=processed_folder, AOI_name=tar_gz_stem)

        upload_zip_to_s3((processed_folder.parent / tar_gz_stem).absolute().__str__() + '.tar.gz',
                         'stephenbucketsagemaker', tar_gz_name) # Todo click
        # clear the unzipped and processed files because they take up a lot of space
        shutil.rmtree(processed_folder)
        shutil.rmtree(unzipped_folder)


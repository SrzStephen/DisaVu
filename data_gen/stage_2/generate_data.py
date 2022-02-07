import requests
import tarfile
from pathlib import Path
import boto3
import shutil
import subprocess


def make_zip(processed_dir: Path):
    # Compresses data
    print(f"making zip ")
    shutil.make_archive(base_name=(processed_dir.parent).__str__(),
                        format='gztar',
                        root_dir=processed_dir
                        )


def upload_zip_to_s3(zip_file: Path, bucket_name: str, file_name: str) -> None:
    print(f"uploading {file_name}")
    s3 = boto3.client('s3')
    with open(zip_file, 'rb') as fp:
        s3.upload_fileobj(fp, bucket_name, file_name, ExtraArgs=dict(RequestPayer='requester',

                                                                     ACL='public-read'))


def download_file(download_loc: Path, download_link: str, tar_name: str) -> None:
    if not download_loc.exists():
        download_loc.mkdir(parents=True)

    file_name = download_loc / tar_name
    if not file_name.exists():
        # credit to https://gist.github.com/devhero/8ae2229d9ea1a59003ced4587c9cb236 for this one
        # The original way I was going about this was dumb
        # thanks bhuiyanmobasshir94
        print("Downloading data. This will take a while (17GB)")
        with open(file_name, 'wb') as fp:
            response = requests.get(download_link, stream=True)
            for chunk in response.raw.stream(1024, decode_content=False):
                if chunk:
                    fp.write(chunk)
                    fp.flush()
    print(file_name)

    tarfile.open(file_name).extractall()


def run_rust_feature_extractor(data_dir: Path, imsize: int):
    out_dir = data_dir / "output"
    if not out_dir.exists():
        out_dir.mkdir(parents=True)

    data_str = data_dir.__str__()
    print("running rust feature extractor binary")
    result = subprocess.run([
        (Path().resolve() / 'xview2_feature_extractor').__str__(),
        "--labels-dir",
        f"{data_str}/labels",
        "--output-dir",
        f"{out_dir}",
        "--images-dir",
        f"{data_str}/images",
        "--output-size",
        str(imsize),
        "--labels-prefix",
        "hurricane"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        raise OSError(result.stderr)


if __name__ == "__main__":
    # Owners of this dataset have this to say
    # - Do not distribute download links or embed download functionality into online services or cloud instances.
    # - If you wish to share the dataset, direct users to xview2.org to sign up, review terms, and download.
    # The dataset is CC BY-NC-SA 4.0, the signup process is extremely easy.
    # Please use the Challenge training set (~7.8 GB) although you could probably get better results by augmenting
    # other datasets from the challenge.
    download_link = "REDACTED"
    download_dir = Path().resolve() / "download"
    tar_name = 'train_images_labels_targets.tar'
    d_dir = download_dir / tar_name.split('.')[0] / "train"
    download_file(download_dir,download_link,tar_name)
    # We've split the next stage of the processing out of pyhton and into rust because otherwise it's really slow,
    # even with all the threads we can give it
    # This will generate a mask png from each of the geojsons that are hurricanes.
    # It will be one mask per poly in the geojson so it'll generate a lot of files!
    image_size = 256
    run_rust_feature_extractor(d_dir, image_size)
    # These are just bloat now that data is processed. Remove them.
    for useless_dir in [d_dir / "images", d_dir / "targets"]:
        shutil.rmtree(useless_dir)
    make_zip(d_dir)
    upload_zip_to_s3(zip_file=download_dir/ f'{tar_name.split(".")[0]}.tar.gz',
                     bucket_name="stephenbucketsagemaker",
                     file_name="xview2_damage_train_data.tar.gz")

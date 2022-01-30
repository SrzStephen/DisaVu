import ogr
import shapely
import gdal
from osgeo import gdal, osr
from xml.dom import minidom
from osgeo import osr, ogr, gdal
import xmltodict, json
from imageio import imread
from osgeo.osr import CoordinateTransformation
from skimage import measure
from skimage.color.colorconv import rgb2gray, rgba2rgb
from shapely.geometry import shape, Point, Polygon, LineString
import geojson
from pathlib import Path
from PIL import Image
from numpy import asarray
import numpy as np
from typing import List, Tuple
from typing_extensions import Literal
import geopandas
from random import choice
from pyproj import Proj
from pyproj import transform as pyproj_transform


def mask_2_poly(mask: Path) -> List[Polygon]:
    # Note Mask assumption is 3 = interior, so scrub anything that isn't that.
    return_list = []
    img = Image.open(mask)
    arr = asarray(img)
    arr = np.where(arr == 3, 255, 0)
    for found_obj in measure.find_contours(arr, 1.0):
        try:
            poly = Polygon(found_obj).simplify(1)
            if poly.is_valid:
                return_list.append(poly)
        except ValueError:
            # it's possible for the simplified poly to be... weird
            # ValueError: A LinearRing must have at least 3 coordinate tuples
            pass
    return return_list


def transform_from_xml(xml: str) -> Tuple[CoordinateTransformation, List[float]]:
    # TODO remove OSR coordinate transforms, no longer needed because that way was annoying and dumb
    with open(xml) as fp:
        xml_data = xmltodict.parse(fp.read())
        target = osr.SpatialReference()
        target.ImportFromProj4(xml_data['PAMDataset']['SRS']["#text"])

    source = osr.SpatialReference()
    source.ImportFromEPSG(4326)  # WGS84

    return osr.CoordinateTransformation(source, target), [float(x) for x in
                                                          xml_data['PAMDataset']['GeoTransform'].split(',')]


def coord_convert(geo_matrix, x, y, to_val=Literal['Pixel', 'World']):
    # https://pcjericks.github.io/py-gdalogr-cookbook/raster_layers.html
    """
    Uses a gdal geomatrix (gdal.GetGeoTransform()) to calculate
    the pixel location of a geospatial coordinate

    use:
     point = ogr.Geometry(ogr.wkbPoint)
    point.Transform(transform)
    # for world2pix on AOI_2_Vegas_img13
    #point.AddPoint(36.128294999699996, -115.3075149)
    point.AddPoint(1, 1)
    point.Transform(transform)
    # point_pixel = ogr.Geometry(org.wkbP)
    x, y = coord_convert(geotransform, point.GetX(), point.GetY(), to_val='World')
    """
    ul_x = geo_matrix[0]
    ul_y = geo_matrix[3]
    x_dist = geo_matrix[1]
    y_dist = geo_matrix[5]
    if to_val == 'Pixel':
        return int((x - ul_x) / x_dist), -int((ul_y - y) / y_dist)
    if to_val == 'World':
        return y * x_dist + ul_x, x * y_dist + ul_y


def pix_poly_to_latlon_pol(geo_matrix: List[float], poly: Polygon) -> Polygon:
    #

    lon_list = []
    lat_list = []
    x, y = poly.exterior.coords.xy
    for x_val, y_val in zip(x, y):
        lon, lat = coord_convert(geo_matrix, x_val, y_val, to_val='World')
        lat_list.append(lat)  # lat and lon are right here but not sure of order in poly. TODO
        lon_list.append(lon)
    return Polygon([[ln, la] for la, ln in zip(lat_list, lon_list)])  # todo did I cook lat lons order like I usually do
    #return Polygon([EPSG_3_to_EPSG_4(lat=la,lon=ln,in_proj=Proj('epsg:3857'),out_proj=Proj('epsg:4326')) for la, ln in zip(lat_list, lon_list)])


# For testing purposes with Rico.
def list_of_polys_to_geojson(polys: List[Polygon]) -> dict:
    poly_geojson = geopandas.GeoSeries(polys).__geo_interface__
    # Add in EPSG3857 coordinates

    return poly_geojson


# unpythonic name, fight me
def EPSG_3_to_EPSG_4(lat: float, lon: float, in_proj: Proj, out_proj: Proj) -> List[float]:
    """Ok background on this wild wide:
    Geojson spec is EPSG4326 which is why when plugged into google maps the coords look
    fine, becuase it (and leaflet) use EPSG:3857 causing things to look like they're in the wrong place
    I really want to flag this https://gis.stackexchange.com/a/48952 because it makes a LOT of sense
."""
    data = list(pyproj_transform(out_proj, in_proj, lat, lon))
    data.reverse()

    return data


def test_png_to_latlon():
    my_jpg = "/home/stephen/AwsMLHack/data/processed/img/AOI_2_Vegas_img1.jpg"
    my_xml = "/home/stephen/AwsMLHack/data/processed/img/AOI_2_Vegas_img13.jpg.aux.xml"
    my_mask = "/home/stephen/AwsMLHack/data/processed/img/AOI_2_Vegas_img13.png"


# if __name__ == "__main__":
#     test_png_to_latlon()
#     my_mask = Path("/home/stephen/AwsMLHack/data/processed/mask/AOI_2_Vegas_img30.png")
#     # print(mask_2_poly(Path(my_mask)))
#     transform, geomatrix = transform_from_xml(
#         "/home/stephen/AwsMLHack/data/processed/img/AOI_2_Vegas_img30.jpg.aux.xml")
#     polys = mask_2_poly(my_mask)
#     latlon_poly = pix_poly_to_latlon_pol(transform, geomatrix, polys[0])
#     latlon_polys = [pix_poly_to_latlon_pol(transform, geomatrix, p) for p in polys]
#     list_of_polys_to_geojson(out_file_name="", polys=latlon_polys)
if __name__ == "__main__":
    latlon_polys_good = []
    latlon_polys_bad = []

    for file in Path("/home/stephen/AwsMLHack/data/processed/img/").glob("*.xml"):
        file_name = file.name.split(".")[0]
        transform, geomatrix = transform_from_xml(
            f"/home/stephen/AwsMLHack/data/processed/img/{file_name}.jpg.aux.xml")
        my_mask = Path(f"/home/stephen/AwsMLHack/data/processed/mask/{file_name}.png")
        polys = mask_2_poly(my_mask)
        if polys:
            latlon_poly = pix_poly_to_latlon_pol(geomatrix, polys[0])
            if range(0,10) == 1:
                latlon_polys_bad += [pix_poly_to_latlon_pol(geomatrix, p) for p in polys]
            else:
                latlon_polys_good += [pix_poly_to_latlon_pol(geomatrix, p) for p in polys]
    with open("good.geojson", 'w') as fp:
        json.dump(list_of_polys_to_geojson(polys=latlon_polys_good), fp)
    with open("bad.geojson", 'w') as fp:
        json.dump(list_of_polys_to_geojson(polys=latlon_polys_bad), fp)

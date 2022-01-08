import ogr
import shapely
import gdal
from osgeo import gdal, osr
from xml.dom import minidom
from osgeo import osr, ogr, gdal
import xmltodict, json


def tif_to_latlon():
    pass

def png_to_latlon(png:str,xml:str):
    xml_val = minidom.parse(xml)
    with open(xml) as fp:

        # MAP coordinates
        dst_src = osr.SpatialReference()
        dst_src.ImportFromEPSG(4326)

        # Pixel_corrds
        xml_data = fp.read()
        file_src = osr.SpatialReference()
        file_src.ImportFromWkt(xml_data)

        # Go from pixel coords to
        ct = osr.CoordinateTransformation(dst_src, file_src)
        point =  ogr.Geometry(ogr.wkbPoint)
        point.AddPoint(1,1)
        point.Transform(ct)
        print(point.GetX())




# https://pcjericks.github.io/py-gdalogr-cookbook/raster_layers.html
def test1_png_to_latlon(png:str,xml:str):
    def world_to_pixel(geo_matrix, x, y):
        """
        Uses a gdal geomatrix (gdal.GetGeoTransform()) to calculate
        the pixel location of a geospatial coordinate
        """
        ul_x = geo_matrix[0]
        ul_y = geo_matrix[3]
        x_dist = geo_matrix[1]
        y_dist = geo_matrix[5]
        pixel = int((x - ul_x) / x_dist)
        line = -int((ul_y - y) / y_dist)
        return pixel, line

    with open(xml) as fp:
        xml_data = xmltodict.parse(fp.read())


        target = osr.SpatialReference()
        target.ImportFromProj4(xml_data['PAMDataset']['SRS']["#text"])
        geotransform = [float(x) for x in xml_data['PAMDataset']['GeoTransform'].split(',')]

    # Extract target reference from the tiff file

    source = osr.SpatialReference()
    source.ImportFromEPSG(4326)

    transform = osr.CoordinateTransformation(source, target)



    point = ogr.Geometry(ogr.wkbPoint)
    point.AddPoint(36.128294999699996, -115.3075149)
    point.Transform(transform)
    #point_pixel = ogr.Geometry(org.wkbP)
    x, y = world_to_pixel(geotransform, point.GetX(), point.GetY())
    print(x, y)


def test_tif_to_latlon(tif:str, mask:str):
    pass

def test_png_to_latlon():
    my_jpg = "/home/stephen/AwsMLHack/data/processed/img/AOI_2_Vegas_img1.jpg"
    my_xml = "/home/stephen/AwsMLHack/data/processed/img/AOI_2_Vegas_img1.jpg.aux.xml"
    my_mask  = "/home/stephen/AwsMLHack/data/processed/img/AOI_2_Vegas_img13.png"
    test1_png_to_latlon(png=my_mask,xml=my_xml)



if __name__ == "__main__":
    test_png_to_latlon()
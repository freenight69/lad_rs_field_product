#!/usr/bin/env python
# -*- coding: utf-8 -*-
import numpy as np
import math
import matplotlib.image as mpimg
from osgeo import gdal
import os
import utils.helper as hp
from coor_trans.coord_transform import gcj02tobd09, bd09togcj02, wgs84togcj02, gcj02towgs84, wgs84tomercator, mercatortowgs84, \
    bd09tomercator, mercatortobd09


class Point(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y


def affine_abc(pixel_points, geo_points):
    n = len(pixel_points)
    pixelX_square = 0.0
    pixelX_pixelY = 0.0
    pixelY_square = 0.0
    pixelX = 0.0
    pixelY = 0.0
    pixelX_geoX = 0.0
    pixelY_geoX = 0.0
    geoX = 0.0
    for i in range(0, n):
        pixelX_square += math.pow(pixel_points[i].x, 2)
        pixelX_pixelY += pixel_points[i].x * pixel_points[i].y
        pixelY_square += math.pow(pixel_points[i].y, 2)
        pixelX += pixel_points[i].x
        pixelY += pixel_points[i].y
        pixelX_geoX += pixel_points[i].x * geo_points[i].x
        pixelY_geoX += pixel_points[i].y * geo_points[i].x
        geoX += geo_points[i].x
    a = np.array([[pixelX_square, pixelX_pixelY, pixelX], [pixelX_pixelY, pixelY_square, pixelY], [pixelX, pixelY, n]])
    b = np.array([[pixelX_geoX], [pixelY_geoX], [geoX]])
    at = np.linalg.inv(a)
    result = at.dot(b)
    return result[0, 0], result[1, 0], result[2, 0]


def affine_def(pixel_points, geo_points):
    n = len(pixel_points)
    pixelX_square = 0.0
    pixelX_pixelY = 0.0
    pixelY_square = 0.0
    pixelX = 0.0
    pixelY = 0.0
    pixelX_geoY = 0.0
    pixelY_geoY = 0.0
    geoY = 0.0
    for i in range(0, n):
        pixelX_square += math.pow(pixel_points[i].x, 2)
        pixelX_pixelY += pixel_points[i].x * pixel_points[i].y
        pixelY_square += math.pow(pixel_points[i].y, 2)
        pixelX += pixel_points[i].x
        pixelY += pixel_points[i].y
        pixelX_geoY += pixel_points[i].x * geo_points[i].y
        pixelY_geoY += pixel_points[i].y * geo_points[i].y
        geoY += geo_points[i].y
    a = np.array([[pixelX_square, pixelX_pixelY, pixelX], [pixelX_pixelY, pixelY_square, pixelY], [pixelX, pixelY, n]])
    b = np.array([[pixelX_geoY], [pixelY_geoY], [geoY]])
    at = np.linalg.inv(a)
    result = at.dot(b)
    return result[0, 0], result[1, 0], result[2, 0]


def width_height(path_str):
    img = mpimg.imread(path_str)
    return len(img[0]), len(img)


def abc_def(path_str):
    pfw = open(path_str, 'r')
    affineOption = pfw.readlines()
    pfw.close()
    a = float(affineOption[0].strip('\n'))
    d = float(affineOption[1].strip('\n'))
    b = float(affineOption[2].strip('\n'))
    e = float(affineOption[3].strip('\n'))
    c = float(affineOption[4].strip('\n'))
    f = float(affineOption[5].strip('\n'))
    return a, b, c, d, e, f


def transform_imgfile(read_path_str, write_path_str, coord_original, coord_target):
    if write_path_str is None:
        raise ValueError("ERROR!!! Parameter result file path not correctly defined")

    # Generate TFW files
    hp.generate_tfw(read_path_str, "")

    tifFile = read_path_str
    tfwFile = read_path_str.split('.')[0] + ".tfw"

    if tifFile[:-4] == tfwFile[:-4]:
        proj, geotrans, data = hp.read_img(tifFile)
        in_ds = gdal.Open(tifFile)
        in_band = in_ds.GetRasterBand(1)
        width = in_band.XSize
        heigth = in_band.YSize

        a, b, c, d, e, f = abc_def(tfwFile)
        p0 = [width / 4, heigth / 4]
        p1 = [width / 4 + width / 2, heigth / 4]
        p2 = [width / 4 + width / 2, heigth / 4 + heigth / 2]
        p3 = [width / 4, heigth / 4 + heigth / 2]
        go0 = [a * p0[0] + b * p0[1] + c, d * p0[0] + e * p0[1] + f]
        go1 = [a * p1[0] + b * p1[1] + c, d * p1[0] + e * p1[1] + f]
        go2 = [a * p2[0] + b * p2[1] + c, d * p2[0] + e * p2[1] + f]
        go3 = [a * p3[0] + b * p3[1] + c, d * p3[0] + e * p3[1] + f]
        # 坐标系转换
        if coord_original == 'gcj02' and coord_target == 'wgs84':
            gt0 = gcj02towgs84(go0[0], go0[1])
            gt1 = gcj02towgs84(go1[0], go1[1])
            gt2 = gcj02towgs84(go2[0], go2[1])
            gt3 = gcj02towgs84(go3[0], go3[1])
        elif coord_original == 'wgs84' and coord_target == 'gcj02':
            gt0 = wgs84togcj02(go0[0], go0[1])
            gt1 = wgs84togcj02(go1[0], go1[1])
            gt2 = wgs84togcj02(go2[0], go2[1])
            gt3 = wgs84togcj02(go3[0], go3[1])
        elif coord_original == 'gcj02' and coord_target == 'bd09':
            gt0 = gcj02tobd09(go0[0], go0[1])
            gt1 = gcj02tobd09(go1[0], go1[1])
            gt2 = gcj02tobd09(go2[0], go2[1])
            gt3 = gcj02tobd09(go3[0], go3[1])
        elif coord_original == 'bd09' and coord_target == 'gcj02':
            gt0 = bd09togcj02(go0[0], go0[1])
            gt1 = bd09togcj02(go1[0], go1[1])
            gt2 = bd09togcj02(go2[0], go2[1])
            gt3 = bd09togcj02(go3[0], go3[1])
        elif coord_original == 'wgs84' and coord_target == 'bd09':
            gtm0 = wgs84togcj02(go0[0], go0[1])
            gtm1 = wgs84togcj02(go1[0], go1[1])
            gtm2 = wgs84togcj02(go2[0], go2[1])
            gtm3 = wgs84togcj02(go3[0], go3[1])
            gt0 = gcj02tobd09(gtm0[0], gtm0[1])
            gt1 = gcj02tobd09(gtm1[0], gtm1[1])
            gt2 = gcj02tobd09(gtm2[0], gtm2[1])
            gt3 = gcj02tobd09(gtm3[0], gtm3[1])
        elif coord_original == 'bd09' and coord_target == 'wgs84':
            gtm0 = bd09togcj02(go0[0], go0[1])
            gtm1 = bd09togcj02(go1[0], go1[1])
            gtm2 = bd09togcj02(go2[0], go2[1])
            gtm3 = bd09togcj02(go3[0], go3[1])
            gt0 = gcj02towgs84(gtm0[0], gtm0[1])
            gt1 = gcj02towgs84(gtm1[0], gtm1[1])
            gt2 = gcj02towgs84(gtm2[0], gtm2[1])
            gt3 = gcj02towgs84(gtm3[0], gtm3[1])
        elif coord_original == 'bd09mc' and coord_target == 'wgs84':
            bd09ll0 = mercatortobd09(go0[0], go0[1])
            bd09ll1 = mercatortobd09(go1[0], go1[1])
            bd09ll2 = mercatortobd09(go2[0], go2[1])
            bd09ll3 = mercatortobd09(go3[0], go3[1])

            gtm0 = bd09togcj02(bd09ll0[0], bd09ll0[1])
            gtm1 = bd09togcj02(bd09ll1[0], bd09ll1[1])
            gtm2 = bd09togcj02(bd09ll2[0], bd09ll2[1])
            gtm3 = bd09togcj02(bd09ll3[0], bd09ll3[1])
            gt0 = gcj02towgs84(gtm0[0], gtm0[1])
            gt1 = gcj02towgs84(gtm1[0], gtm1[1])
            gt2 = gcj02towgs84(gtm2[0], gtm2[1])
            gt3 = gcj02towgs84(gtm3[0], gtm3[1])
        else:
            gt0 = [go0[0], go0[1]]
            gt1 = [go1[0], go1[1]]
            gt2 = [go2[0], go2[1]]
            gt3 = [go3[0], go3[1]]
        pl = [Point(p0[0], p0[1]), Point(p1[0], p1[1]), Point(p2[0], p2[1]), Point(p3[0], p3[1])]
        gl = [Point(gt0[0], gt0[1]), Point(gt1[0], gt1[1]), Point(gt2[0], gt2[1]), Point(gt3[0], gt3[1])]
        ar, br, cr = affine_abc(pl, gl)
        dr, er, fr = affine_def(pl, gl)

        # 仿射变换系数
        trans = (cr, ar, dr, fr, br, er)

        hp.write_img(write_path_str, proj, trans, data)

    # Delete TFW file
    os.remove(tfwFile)


def transform_imgfile_batch(read_path_str, write_path_str, coord_original, coord_target):
    if not os.path.exists(write_path_str):
        os.makedirs(write_path_str)

    for in_file in os.listdir(read_path_str):
        if ".tif" in in_file:
            tifFile = os.path.join(read_path_str, in_file)
            out_path = os.path.join(write_path_str, tifFile.split('\\')[-1])
            transform_imgfile(tifFile, out_path, coord_original, coord_target)

    # Delete TFW files
    hp.delete_tfw(read_path_str)

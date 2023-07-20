#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Version: v1.0
Date: 2023-02-09
Authors: Chen G.
"""


import glob
import os
import ee
import yaml
from ftplib import FTP
import coor_trans.img_transform as img_trans
try:
    from osgeo import gdal
    from osgeo import osr
except ImportError:
    import gdal
    import osr


# ---------------------------------------------------------------------------//
# Cloud Mask
# ---------------------------------------------------------------------------//
def mask_clouds(img, MAX_CLOUD_PROBABILITY):
    """
    mask cloud >= MAX_CLOUD_PROBABILITY

    Parameters
    ----------
    img : ee.Image
        image to apply the cloud masking
    MAX_CLOUD_PROBABILITY : odd integer
        max cloud probability

    Returns
    -------
    ee.Image
        Masked image

    """
    clouds = ee.Image(img.get('cloud_mask')).select('probability')
    isNotCloud = clouds.lt(MAX_CLOUD_PROBABILITY)
    return img.updateMask(isNotCloud).copyProperties(img, ["system:time_start"])


def cloud_mask_filter(col, MAX_CLOUD_PROBABILITY):
    """
    A wrapper function for cloud mask filter

    Parameters
    ----------
    col : ee Image collection
        the image collection to be filtered
    MAX_CLOUD_PROBABILITY : odd integer
        max cloud probability

    Returns
    -------
    ee.ImageCollection
        An image collection where a cloud mask filter is applied to each
        image individually

    """

    def _filter(image):
        _filtered = mask_clouds(image, MAX_CLOUD_PROBABILITY)
        return _filtered

    return col.map(_filter)


# ---------------------------------------------------------------------------//
# The masks for the 10m bands sometimes do not exclude bad data at
# scene edges, so we apply masks from the 20m and 60m bands as well.
# ---------------------------------------------------------------------------//
def mask_edges(s2_img):
    """
    masks images from the 20m and 60m bands

    Parameters
    ----------
    s2_img : ee.Image
        image to apply the border noise masking

    Returns
    -------
    ee.Image
        Masked image

    """
    return s2_img.updateMask(s2_img.select('B8A').mask().updateMask(s2_img.select('B9').mask()))


# 影像scale转换函数
def scale_image(image):
    """
    scale images by 10000

    Parameters
    ----------
    image : ee.Image
        image to apply scale

    Returns
    -------
    ee.Image
        Scaled image

    """
    time_start = image.get("system:time_strat")
    image = image.multiply(0.0001)
    image = image.set("system:time_strat", time_start)
    return image


# 读入image
def read_img(filename):
    dataset = gdal.Open(filename)
    im_width = dataset.RasterXSize
    im_height = dataset.RasterYSize
    im_geotrans = dataset.GetGeoTransform()
    im_proj = dataset.GetProjection()
    im_data = dataset.ReadAsArray(0, 0, im_width, im_height)

    im_band = dataset.GetRasterBand(1)
    nodata = im_band.GetNoDataValue()
    im_data[im_data == nodata] = 0

    del dataset
    return im_proj, im_geotrans, im_data


# 写入image
def write_img(filename, im_proj, im_geotrans, im_data):
    if 'int8' in im_data.dtype.name:
        datatype = gdal.GDT_Byte
    elif 'int16' in im_data.dtype.name:
        datatype = gdal.GDT_Int16
    else:
        datatype = gdal.GDT_Float32

    if len(im_data.shape) == 3:
        im_bands, im_height, im_width = im_data.shape
    else:
        im_bands, (im_height, im_width) = 1, im_data.shape

    driver = gdal.GetDriverByName("GTiff")
    dataset = driver.Create(filename, im_width, im_height, im_bands, datatype)

    dataset.SetGeoTransform(im_geotrans)
    dataset.SetProjection(im_proj)

    if im_bands == 1:
        dataset.GetRasterBand(1).WriteArray(im_data)
    else:
        for i in range(im_bands):
            dataset.GetRasterBand(i + 1).WriteArray(im_data[i])

    del dataset


# 生成tfw和prj文件
def generate_tfw(file_path, gen_prj):
    src = gdal.Open(file_path)
    xform = src.GetGeoTransform()

    if gen_prj == 'prj':
        src_srs = osr.SpatialReference()
        src_srs.ImportFromWkt(src.GetProjection())
        src_srs.MorphToESRI()
        src_wkt = src_srs.ExportToWkt()

        prj = open(os.path.splitext(file_path)[0] + '.prj', 'wt')
        prj.write(src_wkt)
        prj.close()

    src = None
    edit1 = xform[0] + xform[1] / 2
    edit2 = xform[3] + xform[5] / 2

    tfw = open(os.path.splitext(file_path)[0] + '.tfw', 'wt')
    tfw.write("%0.14f\n" % xform[1])
    tfw.write("%0.14f\n" % xform[2])
    tfw.write("%0.14f\n" % xform[4])
    tfw.write("%0.14f\n" % xform[5])
    tfw.write("%0.14f\n" % edit1)
    tfw.write("%0.14f\n" % edit2)
    tfw.close()


# 删除tfw和prj文件
def delete_tfw(path):
    for infile in glob.glob(os.path.join(path, '*.tfw')):
        if os.path.isfile(infile):
            os.remove(infile)
    for infile in glob.glob(os.path.join(path, '*.prj')):
        if os.path.isfile(infile):
            os.remove(infile)


# 清空文件夹下文件
def del_file(path_data):
    for i in os.listdir(path_data):
        file_data = path_data + "\\" + i
        if os.path.isfile(file_data):
            os.remove(file_data)
        else:
            del_file(file_data)


# 图像压缩函数
def compress_raster(origin_file, target_file, method="LZW"):
    dataset = gdal.Open(origin_file)
    driver = gdal.GetDriverByName('GTiff')
    driver.CreateCopy(target_file, dataset, strict=1, options=["TILED=YES", "COMPRESS={0}".format(method), "BIGTIFF=YES"])
    del dataset


# 批量图像压缩函数
def compress_raster_batch(path, target_path, method="LZW"):
    """使用gdal进行文件压缩, LZW方法属于无损压缩"""
    # 新建保存文件
    if not os.path.exists(target_path):
        os.makedirs(target_path)

    rasterList = []
    for in_file in os.listdir(path):  # 遍历待裁剪影像路径中每一个文件
        if ".tif" in in_file:
            rasterFile = os.path.join(path, in_file)
            rasterList.append(rasterFile)
    for raster in rasterList:
        outFile = os.path.join(target_path, raster.split('\\')[-1])
        dataset = gdal.Open(raster)
        driver = gdal.GetDriverByName('GTiff')
        driver.CreateCopy(outFile, dataset, strict=1,
                          options=["TILED=YES", "COMPRESS={0}".format(method), "BIGTIFF=YES"])
        del dataset


# 图像坐标系转换+图像压缩
def trans_compress(trans_dir, trans_crs, filename, filepath):
    filepath_trans = os.path.join(trans_dir, filename)
    temp_file = os.path.join(trans_dir, 'temp.tif')
    img_trans.transform_imgfile(filepath, temp_file, "wgs84", trans_crs)
    compress_raster(temp_file, filepath_trans)
    os.remove(temp_file)


# 连接远程FTP并上传文件
def ftp_upload(local_file, remote_filename):
    with open('./configs/ftp_upload.yml', "r", encoding='utf-8') as f:
        yml_data = yaml.safe_load(f)
        
        # FTP服务器信息
        ftp_host = yml_data['ftp_host']  # FTP服务器地址
        ftp_user = yml_data['ftp_user']    # FTP登录用户名
        ftp_passwd = yml_data['ftp_passwd']  # FTP登录密码
        remote_path = yml_data['remote_path']  # 远程FTP路径
        
        # 连接FTP服务器
        try:
            ftp = FTP(ftp_host)
            ftp.login(user=ftp_user, passwd=ftp_passwd)
            print('Successfully connect FTP!')
        except Exception:
            # 打印异常信息
            print('Failed connect FTP!')
        
        
        # 切换到远程目录
        ftp.cwd(remote_path)
        
        # 上传文件
        with open(local_file, "rb") as f:
            ftp.storbinary("STOR " + remote_filename, f)

        # 关闭FTP连接
        ftp.quit()
        print('{} has been uploaded to FTP!'.format(remote_filename))

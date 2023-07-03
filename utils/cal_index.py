#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Version: v1.0
Date: 2023-02-09
Authors: Chen G.
"""


def cal_ndvi(image):
    """
    归一化差值植被指数 NDVI = (NIR - R) / (NIR + R)
    NDVI 是最常用的植被指数。可以用来表征地面植被密集程度和植物的叶绿素含量。NDVI 数值为 -1 到 1, 
    特点：通常正值表示有植被覆盖，数值越高, 植被越密集或叶绿素含量越高。0 和负值表示岩石、裸土、水体等非植被覆盖。
    使用阶段: NDVI 在作物最活跃生长阶段的季节中期最准确，可以用于诊断作物的叶绿素、氮素含量，从而指导合理施用氮肥。

    Parameters
    ----------
    image : ee.Image
        image to calculate NDVI

    Returns
    -------
    ee.Image
        Image with NDVI band
    """
    return image.addBands(
        image.expression(
            '(nir - red) / (nir + red)',
            {
                'red': image.select('B4'),  # RED
                'nir': image.select('B8')   # NIR
            }).rename('NDVI'))


def cal_ndmi(image):
    """
    归一化差值水分指数 NDMI = (NIR - SWIR1) / (NIR + SWIR1)
    NDMI 通过计算近红外与短波红外之间的差异来定量化反映植被冠层的水分含量情况。
    特点：由于植被在短波红外波段对水分的强吸收，导致植被在短波红外波段的反射率相对于近红外波段的反射率要小，因此 NDMI 与冠层水分含量高度相关，
    可以用来估计植被水分含量，而且 NDMI 与地表温度之间存在较强的相关性，因此也常用于分析地表温度的变化情况。
    使用阶段：作物水分含量与地表温度的变化情况。

    Parameters
    ----------
    image : ee.Image
        image to calculate NDMI

    Returns
    -------
    ee.Image
        Image with NDMI band
    """
    return image.addBands(
        image.expression(
            '(nir - swir1) / (nir + swir1)',
            {
                'nir': image.select('B8'),    # NIR
                'swir1': image.select('B11')  # SWIR1
            }).rename('NDMI'))


def cal_ndre(image):
    """
    归一化差异红边植被指数 NDRE = (NIR – RedEdge) / (NIR + RedEdge)
    在高植被区 NDVI 灵敏度较低，也就是 NDVI 的“饱和”现象。为了应对 NDVI 的这个缺陷，就引入了 NDRE。
    特点：用红边波段取代了 NDVI 中的红色波段。红边是红光和近红外波段中间的一个过度波段，是叶绿素在红光区域的吸收和在近红外区域的反射之间的界限。
    使用阶段: NDRE 在高植被区，例如农田作物封行之后，可以更灵敏地反映植被的叶绿素含量。

    Parameters
    ----------
    image : ee.Image
        image to calculate NDRE

    Returns
    -------
    ee.Image
        Image with NDRE band
    """
    return image.addBands(
        image.expression(
            '(nir - redEdge) / (nir + redEdge)',
            {
                'nir': image.select('B8'),      # NIR
                'redEdge': image.select('B5')   # RedEdge
            }).rename('NDRE'))
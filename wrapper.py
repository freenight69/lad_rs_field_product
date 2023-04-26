#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Version: v1.0
Date: 2023-02-09
Authors: Chen G.
Description: A wrapper function to derive the Sentinel-2 MSI
"""

import ee
import geemap
import os
import helper
import cal_index as ci


###########################################
# DO THE JOB
###########################################

def s2_preprocess(params):
    """
    Applies preprocessing to a collection of S2 images to return an analysis ready sentinel-2 data.

    Parameters
    ----------
    params : Dictionary
        These parameters determine the data selection and image processing parameters.

    Raises
    ------
    ValueError


    Returns
    -------
    ee.ImageCollection
        A processed Sentinel-2 image collection

    """

    VPN_PORT = params['VPN_DPORT']
    START_DATE = params['START_DATE']
    END_DATE = params['END_DATE']
    BANDS = params['BANDS']
    ROI = params['ROI']
    MAX_CLOUD_PROBABILITY = params['MAX_CLOUD_PROBABILITY']
    CAL_NDVI = params['CAL_NDVI']
    CAL_NDMI = params['CAL_NDMI']
    CAL_NDRE = params['CAL_NDRE']
    CLIP_TO_ROI = params['CLIP_TO_ROI']
    EXPORT_CRS = params['EXPORT_CRS']
    EXPORT_SCALE = params['EXPORT_SCALE']
    EXPORT_NAME = params['EXPORT_NAME']
    SAVE_LOCAL = params['SAVE_LOCAL']
    RENDER = params['RENDER']
    RESAMPLE_SCALE = params['RESAMPLE_SCALE']
    LOCAL_DIR = params['LOCAL_DIR']

    ###########################################
    # 0. CHECK PARAMETERS
    ###########################################

    if MAX_CLOUD_PROBABILITY is None:
        MAX_CLOUD_PROBABILITY = 100
    if CAL_NDVI is None:
        CAL_NDVI = False
    if CAL_NDMI is None:
        CAL_NDMI = False
    if CAL_NDRE is None:
        CAL_NDRE = False
    if EXPORT_CRS is None:
        EXPORT_CRS = 'EPSG:4326'
    if EXPORT_SCALE is None:
        EXPORT_SCALE = 10
    if RENDER is None:
        RENDER = False
    if RESAMPLE_SCALE is None:
        RESAMPLE_SCALE = 100
        
    # set VPN port
    geemap.set_proxy(port=VPN_PORT)
    try:
        ee.Initialize()
    except:
        ee.Authenticate()
        ee.Initialize()

    bands_required = ['B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B8A', 'B11', 'B12']
    if not any(band in bands_required for band in BANDS):
        raise ValueError("ERROR!!! Parameter BANDS not correctly defined")

    if MAX_CLOUD_PROBABILITY < 0 or MAX_CLOUD_PROBABILITY > 100:
        raise ValueError("ERROR!!! Parameter MAX_CLOUD_PROBABILITY not correctly defined")

    ###########################################
    # 1. DATA SELECTION
    ###########################################

    # select S-2 image collection
    s2_sr = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED') \
        .filterDate(START_DATE, END_DATE) \
        .filterBounds(ROI)

    # Get ImageCollection footprint list
    sizeRaw = s2_sr.size().getInfo()
    imlistRaw = s2_sr.toList(sizeRaw)
    footprintList = []
    for idx in range(0, sizeRaw):
        img = imlistRaw.get(idx)
        img = ee.Image(img)
        footprint = ee.Geometry(img.get('system:footprint'))
        footprintList.append(footprint)

    ###########################################
    # 2. REMOVE CLOUD
    ###########################################

    if 0 <= MAX_CLOUD_PROBABILITY < 100:
        # Sentinel-2 cloud probability ImageCollection
        s2Clouds = ee.ImageCollection('COPERNICUS/S2_CLOUD_PROBABILITY')
        # Filter input collections by desired data range and region.
        criteria = ee.Filter.And(ee.Filter.bounds(ROI), ee.Filter.date(START_DATE, END_DATE))
        s2Sr = s2_sr.filter(criteria).map(helper.mask_edges)
        s2Clouds = s2Clouds.filter(criteria)
        # Join S2 SR with cloud probability dataset to add cloud mask.
        s2SrWithCloudMask = ee.Join.saveFirst('cloud_mask').apply(**{
            'primary': s2Sr,
            'secondary': s2Clouds,
            'condition': ee.Filter.equals(**{
                "leftField": "system:index",
                "rightField": "system:index"})
        })
        s2_sr = helper.cloud_mask_filter(ee.ImageCollection(s2SrWithCloudMask), MAX_CLOUD_PROBABILITY)
        # scale images
        s2_sr = s2_sr.map(helper.scale_image)
    elif MAX_CLOUD_PROBABILITY == 100:
        s2_sr = s2_sr.map(helper.scale_image)

    ###########################################
    # 3. CALCULATE VEGETATION INDEX
    ###########################################

    if CAL_NDVI:
        s2_sr = s2_sr.map(ci.cal_ndvi)
    if CAL_NDMI:
        s2_sr = s2_sr.map(ci.cal_ndmi)
    if CAL_NDRE:
        s2_sr = s2_sr.map(ci.cal_ndre)

    ###########################################
    # 4. OUTPUT
    ###########################################

    # save to local
    if SAVE_LOCAL:
        
        # mosaic image collection
        img = s2_sr.mosaic()
        
        # clip to roi
        if CLIP_TO_ROI:
            img = img.clip(ROI)

        img_raw = img.select(BANDS)
        img_ndvi = img.select('NDVI')
        img_ndmi = img.select('NDMI')
        img_ndre = img.select('NDRE')

        # save raw images to local
        if not os.path.exists(LOCAL_DIR):
            os.makedirs(LOCAL_DIR)
        
        sd = START_DATE.strftime("%Y-%m-%d")
        outputDate = sd.replace('-', '')
        
        filename_raw = os.path.join(LOCAL_DIR, EXPORT_NAME + '_DT_' + outputDate + '.tif')
        filename_ndvi = os.path.join(LOCAL_DIR, EXPORT_NAME + '_DT_ZS_' + outputDate + '.tif')
        filename_ndmi = os.path.join(LOCAL_DIR, EXPORT_NAME + '_DT_NDMI_' + outputDate + '.tif')
        filename_ndre = os.path.join(LOCAL_DIR, EXPORT_NAME + '_DT_NDRE_' + outputDate + '.tif')
        print('Downloading image in {} on {}:'.format(EXPORT_NAME, outputDate))
        if CLIP_TO_ROI:
            # geemap.download_ee_image(img_raw, filename_raw, region=ROI, crs=EXPORT_CRS, scale=EXPORT_SCALE)
            if CAL_NDVI:
                geemap.download_ee_image(img_ndvi, filename_ndvi, region=ROI, crs=EXPORT_CRS, scale=EXPORT_SCALE)
            if CAL_NDMI:
                geemap.download_ee_image(img_ndmi, filename_ndmi, region=ROI, crs=EXPORT_CRS, scale=EXPORT_SCALE)
            if CAL_NDRE:
                geemap.download_ee_image(img_ndre, filename_ndre, region=ROI, crs=EXPORT_CRS, scale=EXPORT_SCALE)
        else:
            # geemap.download_ee_image(img_raw, filename_raw, region=footprintList[idx], crs=EXPORT_CRS, scale=EXPORT_SCALE)
            if CAL_NDVI:
                geemap.download_ee_image(img_ndvi, filename_ndvi, region=footprintList[idx], crs=EXPORT_CRS, scale=EXPORT_SCALE)
            if CAL_NDMI:
                geemap.download_ee_image(img_ndmi, filename_ndmi, region=footprintList[idx], crs=EXPORT_CRS, scale=EXPORT_SCALE)
            if CAL_NDRE:
                geemap.download_ee_image(img_ndre, filename_ndre, region=footprintList[idx], crs=EXPORT_CRS, scale=EXPORT_SCALE)

        # save visualization images to local
        if RENDER:
            rgb_bands = ['B4', 'B3', 'B2']
            if not any(i in rgb_bands for i in BANDS):
                raise ValueError("ERROR!!! Only can convert RGB bands image into an 32-int RGB image")
            img_rgb = img.select(rgb_bands)
            rgbImage = img_rgb.visualize(**{
                'bands': rgb_bands,
                'min': 0.0,
                'max': 0.3
            })
            filename_rgb = os.path.join(LOCAL_DIR, EXPORT_NAME + '_render_RGB_' + outputDate + '.tif')
            print('Downloading Render RGB Image to {}'.format(filename_rgb))
            if CLIP_TO_ROI:
                geemap.ee_export_image(rgbImage, filename=filename_rgb, scale=RESAMPLE_SCALE, crs=EXPORT_CRS, region=ROI)
            else:
                geemap.ee_export_image(rgbImage, filename=filename_rgb, scale=RESAMPLE_SCALE, crs=EXPORT_CRS, region=footprintList[idx])

            if CAL_NDVI:
                ndviImage = img_ndvi.visualize(**{
                    'bands': ['NDVI'],
                    'min': 0.0,
                    'max': 1.0,
                    'palette': ['FFFFFF', 'CE7E45', 'DF923D', 'F1B555', 'FCD163',
                                '99B718', '74A901', '66A000', '529400', '3E8601',
                                '207401', '056201', '004C00', '023B01', '012E01',
                                '011D01', '011301']
                })
                filename_vis_ndvi = os.path.join(LOCAL_DIR, EXPORT_NAME + '_render_NDVI_' + outputDate + '.tif')
                print('Downloading Render NDVI Image to {}'.format(filename_vis_ndvi))
                if CLIP_TO_ROI:
                    # geemap.download_ee_image(ndviImage, filename_vis_ndvi, region=ROI, crs=EXPORT_CRS, scale=RESAMPLE_SCALE, dtype='int32')
                    geemap.ee_export_image(ndviImage, filename=filename_vis_ndvi, scale=RESAMPLE_SCALE, crs=EXPORT_CRS, region=ROI)
                else:
                    # geemap.download_ee_image(ndviImage, filename_vis_ndvi, region=footprintList[idx], crs=EXPORT_CRS, scale=RESAMPLE_SCALE, dtype='int32')
                    geemap.ee_export_image(ndviImage, filename=filename_vis_ndvi, scale=RESAMPLE_SCALE, crs=EXPORT_CRS, region=footprintList[idx])

    return s2_sr

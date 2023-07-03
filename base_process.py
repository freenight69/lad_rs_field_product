#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Version: v1.0
Date: 2023-04-25
Authors: Chen G.
Description: A wrapper function to process the Sentinel-2 MSI of base
"""

import os
import ee
import geemap
import datetime
import utils.wrapper as wrapper


# set VPN port
geemap.set_proxy(port=5188)
try:
    ee.Initialize()
except:
    ee.Authenticate()
    ee.Initialize()
# os.environ['HTTP_PROXY'] = 'http://127.0.0.1:5188'
# os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:5188'
# ee.Authenticate()
# ee.Initialize()

###########################################
# Lingang Preprocessing
###########################################

def lingang_preprocess(queryDate, export_crs, export_dir, trans_dir):
    # sdate = datetime.datetime.strptime(queryDate, "%Y-%m-%d")
    # edate = (sdate + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    edate = datetime.datetime.strptime(queryDate, "%Y-%m-%d")
    sdate = (edate + datetime.timedelta(days=-1)).strftime("%Y-%m-%d")
    
    roi_lingang = ee.Geometry.Polygon(
        [
            [
                [121.9272557765539,30.969638441699253],
                [121.92737618473996,30.969330819148936],
                [121.92811191322484,30.967310829852963],
                [121.92866481320036,30.96561192619595],
                [121.92915086632533,30.964247407084997],
                [121.92937379549213,30.963551806018376],
                [121.92946303648064,30.963284276062442],
                [121.92957450080434,30.962615394148273],
                [121.92968153770049,30.961830620400644],
                [121.92974838145147,30.961255339502486],
                [121.92977069162943,30.960720301648536],
                [121.92974838145147,30.960082616532823],
                [121.92972607126896,30.959418259068045],
                [121.92970827520575,30.9589232616656],
                [121.92970376108195,30.958557643771915],
                [121.9296770235756,30.958294535801684],
                [121.92977963306139,30.958276682644772],
                [121.92986878691084,30.958285589419486],
                [121.94290270159945,30.958771657071875],
                [121.94331300281766,30.958825159241925],
                [121.94332185634936,30.95900350790841],
                [121.9434200263445,30.95910607455388],
                [121.95361794410682,30.962245295562216],
                [121.95498689305097,30.962691162869863],
                [121.94696493732407,30.98148628837643],
                [121.9453507718933,30.98142831616485],
                [121.93528654900459,30.981049347876382],
                [121.93550955254594,30.980474101247065],
                [121.9354158893775,30.98047853440615],
                [121.93479166876405,30.980469629703336],
                [121.93490755479442,30.980144136549402],
                [121.93823850982598,30.97019583826036],
                [121.93829206747408,30.970137893748525],
                [121.93830543518122,30.970075474844624],
                [121.93823408285552,30.970079885348618],
                [121.92776857387717,30.969647422464654],
                [121.9272557765539,30.969638441699253]
            ]
        ]
    )
    
    lingang_parameter = {'START_DATE': sdate,
                        'END_DATE': edate,
                        'BANDS': ['B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B8A', 'B11', 'B12'],
                        'ROI': roi_lingang,
                        'MAX_CLOUD_PROBABILITY': 75,
                        'CAL_NDVI': True,
                        'CAL_NDMI': False,
                        'CAL_NDRE': False,
                        'EXPORT_CRS': export_crs,
                        'EXPORT_SCALE': 10,
                        'EXPORT_NAME': 'lingang',
                        'CLIP_TO_ROI': True,
                        'SAVE_LOCAL': True,
                        'COOR_TRANS': True,
                        'TRANS_CRS': 'gcj02',
                        'RENDER': False,
                        'RESAMPLE_SCALE': 150,
                        'DOWNLOAD_DIR': export_dir,
                        'TRANS_DIR': trans_dir
                        }
    
    # processed s2 collection
    try:
        lingang_processed = wrapper.s2_preprocess(lingang_parameter)
    except Exception:
        # 打印异常信息
        print('No cloudless images in Lingang on %s' % sdate)
    
    
###########################################
# Dancheng Preprocessing
###########################################

def dancheng_preprocess(queryDate, export_crs, export_dir, trans_dir):
    # sdate = datetime.datetime.strptime(queryDate, "%Y-%m-%d")
    # edate = (sdate + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    edate = datetime.datetime.strptime(queryDate, "%Y-%m-%d")
    sdate = (edate + datetime.timedelta(days=-1)).strftime("%Y-%m-%d")
    
    roi_dancheng = ee.Geometry.Polygon(
        [
            [
                [115.16834215367976,33.701872369004235],
                [115.17627043570991,33.70131946914559],
                [115.17652898790209,33.696708742504754],
                [115.19270219396873,33.695469141510074],
                [115.19269776135631,33.69603538868455],
                [115.19635419318811,33.69560736836466],
                [115.19536871569764,33.688972181515396],
                [115.21243366830475,33.68769689871397],
                [115.21305799376336,33.68953402829715],
                [115.20616420338078,33.69058193647584],
                [115.2065387881696,33.696369831239814],
                [115.21456072975056,33.69592841602659],
                [115.21603668394272,33.699732020060445],
                [115.18431015244617,33.70197050776158],
                [115.16892178430702,33.70637164762904],
                [115.16834215367976,33.701872369004235]
            ]
        ]
    )
    
    dancheng_parameter = {'START_DATE': sdate,
                        'END_DATE': edate,
                        'BANDS': ['B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B8A', 'B11', 'B12'],
                        'ROI': roi_dancheng,
                        'MAX_CLOUD_PROBABILITY': 75,
                        'CAL_NDVI': True,
                        'CAL_NDMI': False,
                        'CAL_NDRE': False,
                        'EXPORT_CRS': export_crs,
                        'EXPORT_SCALE': 10,
                        'CLIP_TO_ROI': True,
                        'EXPORT_NAME': 'dancheng',
                        'SAVE_LOCAL': True,
                        'COOR_TRANS': True,
                        'TRANS_CRS': 'gcj02',
                        'RENDER': False,
                        'RESAMPLE_SCALE': 150,
                        'DOWNLOAD_DIR': export_dir,
                        'TRANS_DIR': trans_dir
                        }
    
    # processed s2 collection
    try:
        dancheng_processed = wrapper.s2_preprocess(dancheng_parameter)
    except Exception:
        # 打印异常信息
        print('No cloudless images in Dancheng on %s' % sdate)


###########################################
# Chongming Preprocessing
###########################################

def chongming_preprocess(queryDate, export_crs, export_dir, trans_dir):
    # sdate = datetime.datetime.strptime(queryDate, "%Y-%m-%d")
    # edate = (sdate + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    edate = datetime.datetime.strptime(queryDate, "%Y-%m-%d")
    sdate = (edate + datetime.timedelta(days=-1)).strftime("%Y-%m-%d")
    
    roi_chongming = ee.Geometry.MultiPolygon(
        [
            [
                [
                    [121.33306269168084,31.669574626976132],
                    [121.3426497501584,31.66349241385966],
                    [121.34483474448706,31.66603857855601],
                    [121.34598516596186,31.665111075626164],
                    [121.3501767263182,31.662582817382308],
                    [121.3534541656061,31.666373034319296],
                    [121.33843147852525,31.675750473994885],
                    [121.33306269168084,31.669574626976132]
                ]
            ],
            [
                [
                    [121.34015711385172,31.76617217014947],
                    [121.35337834281562,31.76393815903682],
                    [121.35567036808607,31.767781880053004],
                    [121.35574610213526,31.76782649132005],
                    [121.35813178675575,31.7719065754877],
                    [121.35631244817212,31.77245505401968],
                    [121.35801138252822,31.775308846423382],
                    [121.34986906356089,31.777685528918695],
                    [121.345427757458,31.77118865267576],
                    [121.34323832394043,31.768058352281738],
                    [121.34155278730978,31.768450763933362],
                    [121.34015711385172,31.76617217014947]
                ]
            ]
        ]
    )
    
    chongming_parameter = {'START_DATE': sdate,
                           'END_DATE': edate,
                           'BANDS': ['B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B8A', 'B11', 'B12'],
                           'ROI': roi_chongming,
                           'MAX_CLOUD_PROBABILITY': 75,
                           'CAL_NDVI': True,
                           'CAL_NDMI': False,
                           'CAL_NDRE': False,
                           'EXPORT_CRS': export_crs,
                           'EXPORT_SCALE': 10,
                           'CLIP_TO_ROI': True,
                           'EXPORT_NAME': 'chongming',
                           'SAVE_LOCAL': True,
                           'COOR_TRANS': True,
                           'TRANS_CRS': 'gcj02',
                           'RENDER': False,
                           'RESAMPLE_SCALE': 150,
                           'DOWNLOAD_DIR': export_dir,
                           'TRANS_DIR': trans_dir
                           }
    
    # processed s2 collection
    try:
        chongming_processed = wrapper.s2_preprocess(chongming_parameter)
    except Exception:
        # 打印异常信息
        print('No cloudless images in Chongming on %s' % sdate)

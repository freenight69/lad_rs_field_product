#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Version: v1.0
Date: 2023-04-25
Authors: Chen G.
Description: A program file to process the Sentinel-2 data of each base daily
"""

import argparse
import datetime
from pathlib import Path
import base_process as bp


"""
python run.py --queryDate 2023-06-01 --export_crs EPSG:4326 --export_dir J:/geoserver_data/ndvi_wgs84 --trans_dir J:/geoserver_data/ndvi_gcj02
"""


parser = argparse.ArgumentParser(description='Process Sentinel-2 data of each base daily')
# parser.add_argument('--queryDate', default=datetime.datetime.now().strftime("%Y-%m-%d"), help='Query date')
parser.add_argument('--queryDate', default='2023-06-16', help='Query date')
parser.add_argument('--export_crs', default="EPSG:4326", help='Export coordinate system')
parser.add_argument(
    '--export_dir', 
    type=Path, 
    default='G:/geoserver_satellite_data/ndvi_wgs84', 
    help='the output directory')
parser.add_argument(
    '--trans_dir', 
    type=Path, 
    default='G:/geoserver_satellite_data/ndvi_gcj02', 
    help='the coordinate transformed images output directory')

opt = parser.parse_args()

if __name__ == '__main__':
    bp.lingang_preprocess(opt.queryDate, opt.export_crs, opt.export_dir, opt.trans_dir)
    bp.dancheng_preprocess(opt.queryDate, opt.export_crs, opt.export_dir, opt.trans_dir)
    bp.chongming_preprocess(opt.queryDate, opt.export_crs, opt.export_dir, opt.trans_dir)
    
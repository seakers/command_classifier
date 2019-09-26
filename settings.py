# -*- coding: utf-8 -*-

import os

DATABASE = {
    'drivername': 'postgres',
    'host': 'localhost',
    'port': '5432',
    'username': os.environ['USER'],
    'password': os.environ['PASSWORD'],
    'database': 'daphne'
}
#!/usr/bin/python3
# coding=utf8

import logging

logging.basicConfig(level=logging.INFO,
                    datefmt='%Y/%m/%d %H:%M:%S',
                    format='%(asctime)s - %(name)s - %(levelname)s - %(lineno)d - %(module)s - %(message)s'
                    )

logger = logging.getLogger(__name__)


#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Config Modul
"""
import json
class Read(object):
    """To get the Config File"""
    def __init__(self, **kwargs):
        """init method"""
        return super().__init__(**kwargs)
    def Config(path):
        """read a config.json"""
        return json.loads(open(path, 'r', 2).read())

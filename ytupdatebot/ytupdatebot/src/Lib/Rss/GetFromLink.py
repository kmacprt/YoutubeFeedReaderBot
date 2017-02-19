#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""get from Link"""
import feedparser
def Parse(rsslink):
    return feedparser.parse(rsslink)
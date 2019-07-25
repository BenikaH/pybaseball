#!/bin/python

from baseball_scraper import fangraphs
import math


def test_instances():
    avail = fangraphs.Scraper.instances()
    print(avail)
    assert(len(avail) == 6)
    assert('THE BAT (RoS)' in avail)
    assert('Steamer (RoS)' in avail)


def test_scrape(fg):
    df = fg.scrape(13611)
    print(df)
    assert(df['HR'][0] == 11)
    assert(df['RBI'][0] == 35)
    assert(df['SB'][0] == 8)
    assert(math.isclose(df['AVG'][0], 0.298))


def test_scrape_multi(fg):
    df = fg.scrape("13590")
    assert(df.Name[0] == "Jesse Winker")
    df = fg.scrape("13611")
    assert(df.Name[0] == "Mookie Betts")

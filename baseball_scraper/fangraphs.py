import shutil
import pandas as pd
import importlib.resources as pkg_resources
from selenium.webdriver.common.by import By
from baseball_scraper import selenium_helper


class Scraper:
    instance_map = {"Steamer (RoS)": "steamerr",
                    "Steamer (Update)": "steameru",
                    "ZiPS (Update)": "uzips",
                    "Steamer600 (Update)": "steamer600u",
                    "Depth Charts (RoS)": "rfangraphsdc",
                    "THE BAT (RoS)": "rthebat"}
    download_file = "FanGraphs Leaderboard.csv"

    """Pulls baseball stats for a single player from fangraphs.com

    :param instance: What data source we are going to pull from.  See
    instances() for a list of available names.
    :type instance: str
    """
    def __init__(self, instance):
        self._set_instance_uri(instance)
        self.df_source = None  # File name to read the csv data from
        self.df = None
        self.dlr = selenium_helper.Downloader(self._uri(), self.download_file)

    def __getstate__(self):
        return (self.instance_uri, self.df)

    def __setstate__(self, state):
        (self.instance_uri, self.df) = state
        self.df_source = None
        self.dlr = selenium_helper.Downloader(self._uri(), self.download_file)

    def scrape(self, player_id):
        """Generate a DataFrame of the stats that we pulled from fangraphs.com

        :param player_id: FanGraphs ID of the player you want to scrape.
        :type player_id: str
        :return: panda DataFrame of stat categories for the player.  Returns an
           empty DataFrame if projection system is not found.
        :rtype: DataFrame
        """
        self._cache_source()
        if str(self.df.playerid.dtype) == "int64":
            return self.df[self.df.playerid == int(player_id)].reset_index()
        else:
            return self.df[self.df.playerid == str(player_id)].reset_index()

    @classmethod
    def instances(cls):
        """Return a list of available data instances for the player

        A data instance can be historical data of a particular year/team or it
        can be from a prediction system.

        :return: Names of the available sources
        :rtype: list(str)
        """
        return cls.instance_map.keys()

    def set_source(self, s):
        self.df_source = s

    def save_source(self, f):
        shutil.copy(self.dlr.downloaded_file(), f)

    def load_fake_cache(self):
        sample_file = 'sample.fangraphs.leaderboard.csv'
        with pkg_resources.open_binary('baseball_scraper', sample_file) as fo:
            self.df = None
            self.df_source = fo
            self._cache_source()

    def _set_instance_uri(self, instance):
        if instance not in self.instance_map:
            raise RuntimeError("The instance given is not a valid one.  Use " +
                               "instances() to see available ones.")
        self.instance_uri = self.instance_map[instance]

    def _uri(self):
        return "https://www.fangraphs.com/projections.aspx?" + \
            "pos=all&stats=bat&type={}".format(self.instance_uri)

    def _cache_source(self):
        if self.df is None:
            if self.df_source is None:
                self._download()
                self.df_source = self.dlr.downloaded_file()
            self.df = pd.read_csv(self.df_source)

    def _download(self):
        self.dlr.download_by_clicking(By.LINK_TEXT, 'Export Data')

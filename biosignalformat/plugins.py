#!/usr/bin/python
import os
import sys
import ujson as json


class PluginStructure(object):
    """Provides tools for a plugin architecture."""
    def __init__(self, plugin_folder = "./plugins", main_module="__init__"):
        super(PluginStructure, self).__init__()
        self.plugin_folder = plugin_folder
        self.main_module = main_module
        self.plugins = {}

    def search_all_plugins(self, autoload=False):
        possible_plugins = os.listdir(self.plugin_folder)
        possible_order = os.path.join(self.plugin_folder, "order.json")
        if os.path.exists(possible_order):
            possible_plugins = json.loads(open(possible_order, "r"))
        for possible_plugin in possible_plugins:
            self.search_plugin(possible_plugin, autoload)
        return self.plugins

    def search_plugin(self, possible_plugin, autoload=False):
        location = os.path.join(self.plugin_folder, possible_plugin)
        if not os.path.isdir(location) or not self.main_module + ".py" in os.listdir(location):
            return None
        if autoload:
            sys.path.append(os.path.realpath(self.plugin_folder))
            try:
                sys.modules[__name__ + "." + possible_plugin] = __import__(possible_plugin)
            finally:
                del sys.path[-1]
            return sys.modules[__name__ + "." + possible_plugin]
        return True

    def load_all(self):
        plugins = self.search_all_plugins(autoload=True)

PluginStructure.BaseArchitecture = PluginStructure()

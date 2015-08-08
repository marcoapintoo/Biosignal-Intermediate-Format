#!/usr/bin/python
import os
import sys
import imp
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
            return False
        plugin_info = imp.find_module(self.main_module, [location])
        self.plugins[possible_plugin] = plugin_info
        if autoload:
            #print "Plug-in", possible_plugin, "loaded!"
            sys.modules[__name__ + "." + possible_plugin] = self.load_plugin(plugin_info)
        return True

    def load_plugin(self, plugin_info):
        return imp.load_module(self.main_module, *plugin_info)

    def load_all(self):
        plugins = self.search_all_plugins(autoload=True)

PluginStructure.BaseArchitecture = PluginStructure()


#===================================================================================================
# Module hack
# Based on plumbum's hack: ``from plugins.cmd import wavelet``
#===================================================================================================
import sys
from types import ModuleType

class LocalModule(ModuleType):
    #" ""The module-hack that allows us to use ``from plumbum.cmd import some_program``"" "
    __all__ = ()  # to make help() happy
    __package__ = __name__

    def __init__(self, plugins, *args, **kwargs):
        super(LocalModule, self).__init__(*args, **kwargs)
        self.__plugins = plugins

    def __getattr__(self, plugin_name):
        if not self.__plugins.search_plugin(plugin_name, autoload=True):
            raise AttributeError(plugin_name)
        return sys.modules[__name__ + "." + plugin_name]

    __path__ = []
    __file__ = __file__

cmd = LocalModule(PluginStructure.BaseArchitecture, __name__ + ".cmd", LocalModule.__doc__)
sys.modules[cmd.__name__] = cmd

#del sys
del ModuleType
del LocalModule

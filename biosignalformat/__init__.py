#!/usr/bin/python
from base import *
from datatype import *
from archiver import *
from structure import *
from calculated import *
from plugins import *

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
        module = self.__plugins.search_plugin(plugin_name, autoload=True)
        if not module:
            raise AttributeError(plugin_name)
        sys.modules[__name__ + "." + plugin_name] = module
        return module

    __path__ = []
    __file__ = __file__

external = LocalModule(PluginStructure.BaseArchitecture, __name__ + ".external", LocalModule.__doc__)
sys.modules[external.__name__] = external

#del sys
del ModuleType
del LocalModule

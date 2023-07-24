from yapsy.IPlugin import IPlugin
from yapsy.PluginInfo import PluginInfo

class PluginOne(IPlugin):
    def print_name(self):
        
        print("This is plugin 1", PluginInfo.plugin_name)
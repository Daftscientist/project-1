from yapsy.PluginManager import PluginManager
############ DELETE THIS - MAKE MY OWN
# Build the manager
simplePluginManager = PluginManager()
# Tell it the default place(s) where to find plugins
simplePluginManager.setPluginPlaces(["plugins"])
# Load all plugins
simplePluginManager.collectPlugins()

# Activate all loaded plugins
for pluginInfo in simplePluginManager.getAllPlugins():
   simplePluginManager.activatePluginByName(pluginInfo.name)
   pluginInfo.plugin_object

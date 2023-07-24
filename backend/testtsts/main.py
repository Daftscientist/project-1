from yapsy.PluginManager import PluginManager

def main():   
    # Load the plugins from the plugin directory.
    manager = PluginManager()
    manager.setPluginPlaces(["plugins"])
    manager.collectPlugins()
    print("hi")
    # Loop round the plugins and print their names.
    for plugin in manager.getAllPlugins():
        print("hi")
        plugin.plugin_object.print_name()

if __name__ == "__main__":
    main()
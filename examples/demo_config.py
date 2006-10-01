"""
Dumb wrapper around Python ConfigParser
removes need for external config libs but has much less functionality
"""

import ConfigParser


def get_config(config_filename):
    """Reads in ini file and returns dictionary of FIRST section ONLY
    """
    config = ConfigParser.ConfigParser()
    config.read(config_filename)
    config_dict = dict(config.items(config.sections()[0]))
    return config_dict


def main():
    myconfig = get_config('lupy.ini')
    print myconfig

if __name__ == '__main__':
    main()

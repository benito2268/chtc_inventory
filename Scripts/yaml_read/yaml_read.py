import sys
import os
import yaml

class Asset:
    def __init__(self, filename):
        with open(filename, 'r') as infile:

            # as far as I can tell safe_load doesn't have any relevant
            # disadvantages over load() here - maybe it's overkill but might as well
            self.asset = yaml.safe_load(infile)
            self.fqdn = filename.removesuffix('.yaml')


def read_yaml(yaml_dir):
    # for ease of use
    if not yaml_dir.endswith('/'):
        yaml_dir += '/'

    ret = []

    for file in os.listdir(yaml_dir):
        if file.endswith('.yaml'):
            ret.append(Asset(yaml_dir + file))

    return ret


def main():

    if len(sys.argv) != 2:
        print('usage: yaml_read.py <yaml_dir>')
        exit(1)

    yaml_dir = sys.argv[1]
    
    assets = read_yaml(yaml_dir)

if __name__ == '__main__':
    main()

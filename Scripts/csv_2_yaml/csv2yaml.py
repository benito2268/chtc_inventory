import sys
import csv
import yaml

# a wrapper class for quoted yaml string values
# used instead of str so keys are not also quoted
class quoted(str):
    pass

class Asset:
    # a shared (among all Assets) dictionary that maps YAML/dict key names
    # to their corresponding column number in the spreadsheet
    #TODO this does not properly account for keys with the same name in different categories
    key_map = {
        'room'          : 0,
        'rack'          : 1,
        'elevation'     : 2,
        'hostname'      : 3,
        'domain'        : 4,
        'model'         : 5,
        'serial_number' : 6,
        'identifier'    : 7,
        'service_tag'   : 8,
        'uw'            : 9,
        'csl'           : 10,
        'morgridge'     : 11,
        'notes'         : 12,
    }

    # converts an array of strings (row from the csv file) to a dictionary
    # TODO need a way to detect condos
    def __init__(self, csv_row):
        # each asset is represented with a nested dictionary
        self.asset = {
            'acquisition' : {
                'po'            : "",
                'date'          : "",
                'reason'        : "",
                'owner'         : "",
                'fabrication'   : False,    # default is false - script will change if true
            },

            'hardware' : {
                'model'         : "",
                'serial_number' : "",
                'service_tag'   : "",
                'purpose'       : "",
                'notes'         : "",
            },

            'condo_chassis' : {
                'identifier'    : "",
                'model'         : "",
            },

            'location' : {
                'rack'      : "",
                'elevation' : "",
                'room'      : "",
                'building'  : "",
            }, 

            'tags' : {
                'csl'       : "",
                'uw'        : "",
                'morgridge' : "",
            },
        }

        self.hostname = csv_row[self.key_map['hostname']]
        self.domain = csv_row[self.key_map['domain']]

        # iterate through each inner and outer key and grab
        # its corresponding value (as determined by key_map) from the spreadsheet
        # TODO what to do about condo models
        # TODO find location info in puppet repo
        for outer_key, outer_value in self.asset.items():
            if isinstance(outer_value, dict):
                #if outer_value is a dictionary we need to iterate one level deeper
                for inner_key, inner_value in outer_value.items():
                    cell = self.key_map.get(inner_key, "")
                    match cell:
                        case "":
                            value = quoted('MISSING')
                        case _:
                            value = quoted(csv_row[cell])

                    self.asset[outer_key][inner_key] = value
        
        # call any heuristics here to help extract misc. data
        self.asset['acquisition']['po'] = quoted(has_po(csv_row[self.key_map['notes']]))
        self.asset['acquisition']['fabrication'] = is_fabrication(csv_row[self.key_map['notes']])

# for debugging
def print_dict(d):
    print('\n')
    for x in d:
        print(x, end="")

        if isinstance(x, dict):
            for y in d[x]:
                print('\t', y, ':', d[x][y])
        else:
            print(':', d[x])

# the default Python yaml module doesn't preserve double quotes :(
# can change that behavior with a representer
# see "Constructors, representers, resolvers" in https://pyyaml.org/wiki/PyYAMLDocumentation
def quote_representer(dumper, data):
    return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='"')

# a heuristic for trying to determine if an asset
# is a fabrication from its 'notes' field
# params:
#   notes: the notes section from the elevation spreadsheet
#
# returns: True if fabrication, false if not
def is_fabrication(notes):
    return notes.lower().find('fabrication') >= 0

# a heuristic for trying to determine if an asset
# has a PO # from its 'notes' field
# params:
#   notes: the notes section from the elevation spreadsheet
#
# returns: the PO # if one was found - 'MISSING' otherwise
def has_po(notes):
        # we assume it is, try to return the PO
    if notes.lower().find('uw po') >= 0:
        index = notes.find("UW PO")
        index += len("UW PO ")

        return notes[index:]
    else:
        return 'MISSING'

# This function is meant to convert the CHTC inventory spreadsheet
# into an array of Asset objects containing all of it's data
# 
# params: csv_name - name of the input csv file
# returns: a list of Asset objects as read from the file
def csv_read(csv_name): 
    with open(csv_name, newline="") as csvfile:

        # I think the csv module considers this the "excel dialect"
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        assets = []

        # skip labels in the first CSV row
        next(reader)

        for row in reader:
            a = Asset(row)
            assets.append(a)

        return assets

# This function takes a list of Asset objects and generated a YAML file
# for each one
#
# params:
#   assets: the list of assets to generate from
def gen_yaml(assets):
    # register the yaml representer for double quoted strings
    yaml.add_representer(quoted, quote_representer)

    # todo surely there is a better way to construct the name??
    with open(assets[0].hostname + '.' + assets[0].domain + ".yaml", 'w') as testfile:
        yaml.dump(assets[0].asset, testfile)
    
# having a main function might be a good idea?
# if this module is ever imported somewhere
# but this script is also kind of a one off...
def main():
    # take csv filename as a command line arg
    if len(sys.argv) < 2:
        print("usage: csv2yaml.py <csv_file>")
        exit(1)

    csv_name = sys.argv[1]
    assets = csv_read(csv_name)

    gen_yaml(assets)

if __name__ == "__main__":
    main()

# HDB Flat File Generator

hdb_ff_gen creates a suite of flat/static .html files which can be hosted using a simple http server.

## Installation

Clone the repo here: [hdb_ff_gen clone link](https://github.com/beautah/hdb_ff_gen.git) then populate the hdb_api wrapper folder inside by cloning the hdb_api project found here: [hdb_api clone link](https://github.com/beautah/hdb_api.git).

```git
git clone https://github.com/beautah/hdb_ff_gen.git
cd hdb_ff_gen
git clone https://github.com/beautah/hdb_api.git
```

An hdb_config.json file is required to access HDB, contact [Beau Uriona](mailto:buriona@usbr.gov) for information on it's structure. The gis folder can be populated using the public gists located [here](https://gist.github.com/beautah), be sure to download all .topojson and .geojson files. Finally an ff_config.json file must be created, currently the helper file [ff_config_gen.py](https://github.com/beautah/hdb_ff_gen/blob/master/ff_config_gen.py) can assist but eventually a GUI will be created. The format should be easy to follow by looking at [ff_config_gen.py](https://github.com/beautah/hdb_ff_gen/blob/master/ff_config_gen.py).

## Requirements

install the following [requirements](https://github.com/beautah/hdb_ff_gen/blob/master/requirements.txt). For windows users a guide to installing geopandas can be found [here](https://geoffboeing.com/2014/09/using-geopandas-windows/).

```bash
pip install -r path/to/requirements.txt
```

## Usage

A pseudo CLI works as follows:

```bash
python3 path/to/hdb_ff_gen/ff_config_gen.py
python3 path/to/hdb_ff_gen/ff_gen.py config_schema_name
```
Where config_schema_name is the key to the json dict with your desired ff_gen configuration.

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate. In fact please write them as I haven't done any ;)

## License
[MIT](https://choosealicense.com/licenses/mit/)
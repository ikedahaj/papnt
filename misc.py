from typing import Optional
from pathlib import Path
import configparser


def load_config(ini_path:  Optional[str | Path]=None) -> dict:
    def eachsection(parser, section):
        config = dict(parser.items(section))
        for key in config:
            try:
                config[key] = eval(config[key])
            except:
                pass
        return config
    ini_path=ini_path or  (Path(__file__).parent / 'config.ini')
    if not Path(ini_path).exists():
        raise FileNotFoundError(f'Not found: {ini_path}')
    parser = configparser.ConfigParser()
    parser.read(ini_path)
    return {section: eachsection(parser, section)
            for section in parser.sections()}

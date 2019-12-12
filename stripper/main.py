from datetime import datetime
from argparse import ArgumentParser
from stripper.params import Params
from PIL import Image
from stripper.helper import normalizeImg,INTEGER_8BIT_MIN,INTEGER_8BIT_MAX,resize_img
import mrcfile
from numpy import asarray
def run():
    parser = ArgumentParser("stripper parser tool")
    parser.add_argument(dest="config_filename",type=str, nargs='?',help="name of the config_file to use. Default value is 'example_config.json'")
    args=parser.parse_args()
    config_filename = args.config_filename if args.config_filename is not None else "example_config.json"
    print("START:",datetime.now())
    params=Params(config_filename)
    try:
        img=mrcfile.open(params.config_path_to_file).data
    except ValueError:
        img=asarray(Image.open(params.config_path_to_file))

    if params.resize is not None:
        img=resize_img(img=img,resize=params.resize)
    if params.convert8bit is True:
        img=normalizeImg(img=img,new_max=INTEGER_8BIT_MAX,new_min=INTEGER_8BIT_MIN)

    print("END:", datetime.now())

if __name__ == "__main__":
    run()
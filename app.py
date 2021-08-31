from os import path, getcwd, system
from subprocess import Popen
from argparse import ArgumentParser
from app.controllers.images import Images
from app.controllers.products import Products

imgs = Images()
item = Products()

path_public = path.join(getcwd(), 'public')

parser = ArgumentParser()
parser.add_argument('--image', type=int, help='The Product Line')
parser.add_argument('--products', type=int, help='The Product Line')
parser.add_argument('--campanha', type=str, nargs='?', const='all', help='Load Campaigns to Products')
args = parser.parse_args()

if args.campanha is not None:
    if args.campanha == 'all':
        item.add_campanha()
        item.add_product_campanhas()
        item.add_store_shop()

if args.products is not None:
    line = args.products
    if line > 5:
        print(f"[LINE][{line}][WRONG]")
    else:
        item.clean_temp_line(line)
        item.initialize(line)
        item.add_product_store(line)
        item.add_product_image(line)
        pass


if args.image is not None:
    line = args.image
    if line > 5:
        print(f"[LINE][{line}][WRONG]")
    else:
        # imgs.initialize(line)
        imgs.move_image(line)
        path_temp = path.join(path_public, 'temp', f"temp-{line}")
        system(f"optimize-images -rc {path_temp}")
        imgs.upload(line)
        path_banco = path.join(path_public, 'image', f"{line}")
        system(f"optimize-images -rc {path_banco}")

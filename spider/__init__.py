import pkgutil
import sys
from spider import music, vod, live

__modules = [
    music, vod, live
]


def load_all_modules_from_dir(module):
    for importer, package_name, _ in pkgutil.iter_modules(module.__path__, module.__name__ + '.'):
        if package_name not in sys.modules:
            importer.find_module(package_name).load_module(package_name)


for module in __modules:
    load_all_modules_from_dir(module=module)


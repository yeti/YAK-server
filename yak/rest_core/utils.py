from _ssl import SSLError
from swiftclient import ClientException
import importlib


def retry_cloudfiles(method, *args):
    done, tries = False, 0
    while not done:
        try:
            result = method(*args)
            return result
        except SSLError:
            pass
        except ClientException:
            pass

        tries += 1

        # Try at max, 10 times before quitting
        if tries >= 10:
            done = True


def get_class(path):
    path_split = path.split(".")
    module_path = ".".join(path_split[:-1])
    class_name = path_split[-1]
    module = importlib.import_module(module_path)
    _class = getattr(module, class_name)
    return _class
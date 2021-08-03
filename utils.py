import yaml
from munch import Munch

def getConfiguration(conf):
    globalConf = yaml.load(open(conf))
    return Munch.fromDict(globalConf['source'])

import yaml

# Loading mod configure.
with open('cfg/mod.yaml', 'r') as mf:
    mod = yaml.safe_load(mf)

# Loading color configure.
with open('cfg/color.yaml', 'r') as cf:
    color = yaml.safe_load(cf)

# Loading icon configure.
NODE_ICONx85_PATH = 'lib/icon/nodesx85/{}.png'
NODE_ICONx500_PATH = 'lib/icon/nodesx500/{}.png'
with open('cfg/icon.yaml', 'r') as icf:
    icon = yaml.safe_load(icf)

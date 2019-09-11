import yaml

# Loading mod configure.
with open('../cfg/mod.yaml', 'r') as mf:
    mod = yaml.safe_load(mf)

# Loading node database configure.
# with open('../cfg/nodb.yaml', 'r') as nf:
#    nodb = yaml.safe_load(nf)

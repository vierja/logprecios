import os
print os.path.abspath("data/")
print os.path.isabs("data/")
print os.path.basename("../data")
print os.path.basename("../data/algo")
print os.path.commonprefix("../data/algo")
print os.path.commonprefix("../data")
print os.path.dirname("../data/algo")
print os.path.dirname("../data")
print os.path.split("../data/algo")
print os.path.split("../data")
print os.path.normpath("../data/algo")
print os.path.normpath("../data")
print os.path.join(os.path.dirname(__file__), '..', '..', 'resources') 

print os.path.abspath("/Users/javier/Development/tracker-inflacion-uy/tracker/../../resources")


print os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data/"))


import times

print str(times.now())
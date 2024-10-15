import os
from groqModel import get_land_details, get_content


docs = ['deed', 'land_title', 'junction', 'mm', 'land', 'sale']

base_dir = 'vlm'

for doc in docs:
    dir = os.path.join(base_dir, doc)

    content = get_content(dir)

    res = get_land_details(content)

    print(res)
    print()
    print()

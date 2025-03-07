import torch
import torchvision
import matplotlib
import pandas as pd
import PIL
import tqdm

# Define the required packages and their versions
requirements = f"""torch=={torch.__version__}
torchvision=={torchvision.__version__}
matplotlib=={matplotlib.__version__}
pandas=={pd.__version__}
Pillow=={PIL.Image.__version__}
tqdm=={tqdm.__version__}
"""

# Write to requirements.txt
with open("requirements.txt", "w") as f:
    f.write(requirements)

print("requirements.txt has been created!")

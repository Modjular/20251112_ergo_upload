# pyramid.py
import math
import tifffile as tif
from pathlib import Path

def generate_pyramid(filepath: str | Path):
    '''Given a tifffile, export a resolution pyramid at the same location, but with .<name>''' 
    filepath = Path(filepath)
    destpath = filepath.parent / f'.{filepath.stem}'

    if not filepath.name.endswith('.tif'):
        raise Exception('I need a tif')

    if destpath.exists():
        raise Exception(f'{destpath.name} already exists!')

    # In V1, handle only 2D and 3D. In V2, handle the full TZCRVYX
    
    try:
        img = tif.memmap(filepath).squeeze()
        destpath.mkdir()

        assert len(img.shape) == 2 or len(img.shape) == 3
    except Exception as e:
        raise e

    # if 2D, recast to 3D
    if len(img.shape) == 2:
        img = img.reshape(1, img.shape[0], img.shape[1])

    TILE_SIZE = 256
    LEVEL_MAX = 4

    for level in range(LEVEL_MAX + 1):
        for z in range(img.shape[0]):

            # For each z plane, downsize according to the level, then
            # Assumes each zplane will fit in memory*
            # TODO Later, multithread this part. One zplane per thread

            step = 2 ** level
            resized = img[z, ::step, ::step]
            print(resized.shape)

            # Then, split into (TILE_SIZE, TILE_SIZE) tiles
            height = resized.shape[0] # Y
            width = resized.shape[1] # X

            for j in range(math.ceil(height / TILE_SIZE)):
                for i in range(math.ceil(width / TILE_SIZE)):

                    tile = resized[
                        j*TILE_SIZE:(j+1)*TILE_SIZE,
                        i*TILE_SIZE:(i+1)*TILE_SIZE
                    ]

                    tilename = f'L{level}_Z{z}_{j}_{i}.tif'

                    mm = tif.memmap(destpath/tilename, shape=tile.shape, dtype=tile.dtype)
                    mm[:] = tile
                    print(tilename, mm.shape)

 
if __name__ == '__main__':
   generate_pyramid('/Users/tony/projects/20251112_ergo_upload/data/002_IDv3__aa855_s05_c1.tif')

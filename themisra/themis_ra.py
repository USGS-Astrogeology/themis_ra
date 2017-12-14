import glob
import logging
import os
import subprocess
import sys
import time
import pvl

from themisra import MPI

from plio.io import io_gdal, io_hdf, io_json
from plio.date import astrodate, julian2ls, julian2season
import plio.utils
from plio.utils import log
from plio.utils.utils import check_file_exists, find_in_dict
import themisra.utils.utils as util

import themisra.processing.processing as processing

from themisra.wrappers import pipelinewrapper, isiswrapper

#Constants
instrumentmap = {'THERMAL EMISSION IMAGING SYSTEM':'THEMIS'}  #Mapping of instrument names as stored in the header to short names


#Get MPI to abort cleanly in the case of an error
sys_excepthook = sys.excepthook
def mpi_excepthook(v, t, tb):
    sys_excepthook(v, t, tb)
    MPI.COMM_WORLD.Abort(1)
sys.excepthook = mpi_excepthook

def process_image(job, logger=None, bands=[3,9]):
    #Create a temporary working directory
    working_path = plio.utils.utils.create_dir(basedir=job['workingdir'])
    if not logger: print('Working dir created at {}'.format(working_path))
    # ISIS preprocessing
    processing.preprocess_image(job, working_path)
    if not logger: print('Preprocessing completed.')
    # DaVinci processing
    isistemp, isisrad = processing.process_image(job,working_path)
    if not logger: print('Davinci processing completed.')
    processing.map_ancillary(isistemp, job)
    if not logger: print('Ancillary data collection completed.')
    band_a = util.extract_band(job, isistemp, bands[0])
    if band_a is None:
        print('Input image does not contain band {}'.format(bands[0]))
        return
    band_b = util.extract_band(job, isistemp, bands[1])
    if band_b is None:
        print('Input image does not contain band {}'.format(band[1]))
        return

    if not logger: print('Bands {} and {} extracted.'.format(*bands))

    rock_a = util.generate_rad_image(band_a, bands[0])
    rock_b = util.generate_rad_image(band_b, bands[1])
    if not logger: print('Rock {} and rock {} computed.'.format(*bands))
    if not logger: print('Pre- & post-processing complete.')

    return band_a, band_b, rock_a, rock_b

#Setup logging
#log.setup_logging(level=config.LOG_LEVEL)
logger = logging.getLogger(__name__)

def main():
    comm = MPI.COMM_WORLD
    rank = comm.rank
    if rank == 0:
        t_start = time.time()
        #Parse the job input
        if len(sys.argv) < 2:
            logger.error("Please supply an input configuration file.")
            sys.exit()
        logger.info("Processing using {} cores".format(comm.size))
        job = io_json.read_json(sys.argv[1])

        process_image(job)

if __name__ == '__main__':
    main()

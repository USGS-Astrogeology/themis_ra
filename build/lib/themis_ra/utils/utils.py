def preprocessimage(job, workingpath, parameters):
    """
    Preprocess a THEMIS EDR for Davinci using ISIS and write files into the
    workingpath.

    Parameters
    ----------
    job : dict
          A dictionary of job containing an image list and
          processing parameters

    workingpath : str
                  The working directory for intermediate files

    Returns
    -------

    outcube: str
               PATH to the preprocessed images.
    """
    # Check that the image exists
    image = job['images']
    if not check_file_exists(image):
        MPI.COMM_WORLD.Abort(1)

    #TODO Check with Trent - is this dumb to offer reprojection?
    #TODO Add reprojection attempt to get ancillary data into the right form.

    logger.info('Reading image {}'.format(image))

    # Process the image header
    job = process_header(job)
    if job is None:
        MPI.COMM_WORLD.Abort(1)

    basepath, fname = os.path.split(image)
    fname, _ = os.path.splitext(fname)

    #Convert to ISIS
    outcube = os.path.join(workingpath, '{}.cub'.format(fname))
    kernel = job.get('kernel', None)
    isiswrapper.preprocess_for_davinci(image, outcube, kernel)

    return outcube

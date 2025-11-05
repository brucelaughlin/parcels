
def parcels_one_release(seed_date_datetime=None)

    # ------------------------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------------------------
    # Hardcoded paths and values, must change according to input model files and the years they span, seed locations, etc
    # ------------------------------------------------------------------------------------------------------------------------------------
    #
    # ---------------------------------
    # Model data
    # ---------------------------------
    static_file = "/home/blaughli/tracking_project_v2/grid_data/wcr30test1_grd.nc"
    dataset_folder = "/home/blaughli/u_WCR30_forcing_files/wcr30_ERA1_v1_1999_2024"
    dataset_folder_W = "/home/blaughli/symbolic_links_ROMS/WCR30_ERA_v1_1999_2024"
    full_run_first_year = 1999
    full_run_final_year = 2024  
    #
    # ---------------------------------
    # Seed location data
    # ---------------------------------
    #polygon_seed_lon_lat_file = "/home/blaughli/tracking_project_v2/misc/z_boxes/add_Extra_Cells/z_output/combined_oldNew_points_lon_lat_WCR30_singleCellPolygons.p"
    polygon_seed_lon_lat_file = "/home/blaughli/parcels/general_code/polygons_and_seeding/z_output/seeding_latlon_WCR30_withPeteAdditions_romsGridCellCentroidsOnly.p"
    #
    # ------------------------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------------------------


    # ------------------------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------------------------
    # Parcels input and other constants (These don't need to be changed when the above paths and constants change.  Change as desired)
    # ------------------------------------------------------------------------------------------------------------------------------------
    dt_calc_mins = 60
    dt_out_mins = 60
    particle_lifetime_days = 180
    min_float_depth = 20
    depth_step = 2.5
    shallow_seed_depth = 1
    
    chunk_output_particle = int(1e6)
    chunk_output_time = 10
    # ------------------------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------------------------
    

    t_init = time.time()
    print(f"RUNNING one release, seed date: {seed_date_datetime}")
    print(f"Start time: {time.ctime()}")

    current_year = int(seed_date_datetime.year)
    file_index = current_year - full_run_first_year

    # We'll have one parent output directory per year, with child output files named by date within the year
    output_dir_general = f"{os.getcwd()}/z_output_{current_year}"
    os.makedirs(output_dir_general, exist_ok = True)

    dataset_folder_stem = Path(dataset_folder).stem
    seed_date_datetime_str = f"{seed_date_datetime.year}{seed_date_datetime.month}{seed_date_datetime.day}"
    output_file_name_stem = f"{Path(dataset_folder).stem}_oneRelease_{seed_date_datetime_str}"
    output_file_name = os.path.join(output_dir_general,output_file_name_stem)

    model_files = sorted(glob(f'{dataset_folder}/*.nc'))
    model_files_W = sorted(glob(f'{dataset_folder_W}/*.nc'))

    # Use an input file list with a maximum length of 2 (My construction seeds for one year and then lets all floats run for their lifetime, which is assumed to be <1 year)
    if current_year = full_run_final_year:
        model_files = model_files[-1:]
        model_files_W = model_files_W[-1:]
    else:
        model_files = model_files[file_index:file_index + 2]
        model_files_W = model_files_W[file_index:file_index + 2]

    UCSCParticle = parcels.ScipyParticle.add_variables(
        [
        parcels.Variable("age", initial=0),
        parcels.Variable("bottomDepth", initial=0),
        ]
    )

    with Dataset(static_file, 'r') as dset:
        lon_rho = np.array(dset['lon_rho'][:])
        lat_rho = np.array(dset['lat_rho'][:])
        h = np.array(dset['h'][:])

    #--------- Get seeding lon/lat coordinates data ------------
    file = open(polygon_seed_lon_lat_file,'rb')
    list_of_arrays_of_points_in_polygons_lonlat = pickle.load(file)
    file.close
    num_polygons = len(list_of_arrays_of_points_in_polygons_lonlat)

    # ----------------------
    # NEW DEPTH ASSIGNMENT ALGORITHM
    lons_polygons = []
    lats_polygons = []
    for i_polygon in range(num_polygons):
        lons_polygons += list(list_of_arrays_of_points_in_polygons_lonlat[i_polygon][0,:])
        lats_polygons += list(list_of_arrays_of_points_in_polygons_lonlat[i_polygon][1,:])
    h_polygon_points = griddata(np.array((lon_rho.ravel(), lat_rho.ravel())).T, h.ravel(), np.array((lons_polygons, lats_polygons)).T)
    # ----------------------

    zs = []
    lons = []
    lats = []
    horizontal_location_counter = 0
    for i_polygon in range(num_polygons):
        for j_point in range(np.shape(list_of_arrays_of_points_in_polygons_lonlat[i_polygon])[1]):
            bottom_depth = h_polygon_points[horizontal_location_counter]
            depth_min = np.floor(min(min_float_depth,bottom_depth))
            for k_depth in range(int(np.floor(depth_min / depth_step)) + 1):
                if k_depth == 0:
                    zs.append(-1 * shallow_seed_depth)
                else:
                    zs.append(-k_depth*depth_step)
                lons.append(list_of_arrays_of_points_in_polygons_lonlat[i_polygon][0,j_point])
                lats.append(list_of_arrays_of_points_in_polygons_lonlat[i_polygon][1,j_point])
            horizontal_location_counter += 1

    variables = {
        "U":    "u_east",      
        "V":    "v_north",
        "W":    "w",
        "zeta": "zeta",
        "z_rho":"z_rho_plus_2",
        "z_w":  "z_w",
        "H":    "h",
        "landmask": "mask_rho",
    }

    filenames = {
        "U": model_files,
        "V": model_files,
        "W": model_files_W,
        "zeta": model_files,
        "z_rho": model_files,
        "z_w": model_files,
        "H": static_file,   # Note that Clark's WCR30 files contain h as a variable
        "landmask": static_file,
    }

    dimensions = {
        "U":     {"lon":"lon_u",   "lat":"lat_u",   "depth":"not_yet_set", "time":"ocean_time"},
        "V":     {"lon":"lon_v",   "lat":"lat_v",   "depth":"not_yet_set", "time":"ocean_time"},
        "W":     {"lon":"lon_rho","lat":"lat_rho","depth":"not_yet_set", "time":"ocean_time"},
        "zeta":  {"lon":"lon_rho","lat":"lat_rho","time":"ocean_time"},
        "z_rho": {"lon":"lon_rho","lat":"lat_rho","depth":"not_yet_set", "time":"ocean_time"},
        "z_w":   {"lon":"lon_rho","lat":"lat_rho","depth":"not_yet_set", "time":"ocean_time"},
        "H":     {"lon":"lon_rho","lat":"lat_rho"},
        "landmask":     {"lon":"lon_rho","lat":"lat_rho"},
    }

    fieldset = parcels.FieldSet.from_netcdf(filenames, variables, dimensions, mesh="spherical")
    fieldset.landmask.interp_method = "nearest"

    # Now input the true depths:
    # tell Parcels that U/V live on the z_rho field, W on z_w
    fieldset.U.set_depth_from_field(fieldset.z_rho)
    fieldset.V.set_depth_from_field(fieldset.z_rho)
    fieldset.W.set_depth_from_field(fieldset.z_w)

    pset = parcels.ParticleSet(
        fieldset=fieldset, 
        pclass=UCSCParticle,
        lon=lons, 
        lat=lats, 
        depth=zs,
        time = seed_date_datetime,
    )

    kernels = [parcels.AdvectionRK4_3D, parcels_util.AgeAndTidalKick, parcels_util.DepthAdjustmentAndLandmask, parcels_util.DeleteParticle]

    output_file = pset.ParticleFile(name=output_file_name, outputdt=timedelta(minutes=dt_out_mins), chunks = (chunk_output_particle, chunk_output_time))

    t_setup_end = time.time()
    setup_time = t_setup_end-t_init
    total_setuptime_hours = round(setup_time/3600,3)
    print(f"Setup time: {total_setuptime_hours} hours")

    pset.execute(
        kernels,
        dt=timedelta(minutes=dt_calc_mins),
        runtime=timedelta(days=particle_lifetime_days),
        output_file=output_file,
    )

    t_run_end = time.time()
    runtime = t_run_end-t_init
    total_runtime_hours = round(runtime/3600,3)
    print(f"Finished!")
    print(f"Setup time: {total_setuptime_hours} hours")
    print(f"Runtime time: {total_runtime_hours} hours")



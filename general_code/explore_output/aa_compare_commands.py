
%run combine_sort_explore_output.py /home/blaughli/parcels/t_testing/t_test_mpiVsNo_splitSeed/z_output_Mpi__numReleases_2__lifetimeDays_10/wcr30_ERA1_v1_1999__numReleases_2 1

%run combine_sort_explore_output.py /home/blaughli/parcels/t_testing/t_test_mpiVsNo_splitSeed/z_output_noMpi__numReleases_2__lifetimeDays_10





lons_mpi_trim = lons_mpi[:,:-10]
target_sum = np.shape(lons)[0]
num_timesteps_common = np.shape(lons_mpi_trim)[1]
equal_timesteps_list = []
for i_timestep in range(num_timesteps_common):
    #equal_timesteps_list.append(np.sum(lons_mpi[:,i_timestep] == lons[:,i_timestep]) == target_sum)
    #equal_timesteps_list.append(f"{target_sum - np.sum(lons_mpi_trim[:,i_timestep] == lons_nmpi[:,i_timestep])}/{target_sum}")
    equal_timesteps_list.append(f"{np.sum(lons_mpi_trim[:,i_timestep] == lons_nmpi[:,i_timestep])}/{target_sum}")



# Functions to be used as kernels in OceanParcels
# Written by the wonderful double-and-a-half masters holder Bruce Laughlin with most credit actually going to Paul, Chris, and Jordana

def DeleteParticle(particle, fieldset, time):
    if particle.state >= 50:
        #print(f"DELETING, particle state: {particle.state}")
        print(f"\nDELETING, id: {particle.id}, state: {particle.state}, age: {particle.age}, depth: {particle.depth}, (Lon,Lat):   ({particle.lon} , {particle.lat})\n")
        #print(f"\nDELETING, id: {particle.id}, state: {particle.state}, age: {particle.age}, depth: {particle.depth}, lon: {particle.lon}, lat: {particle.lat}, depth: {particle.depth}\n")
        '''
        print("--------------------------------------------")
        print("PARTICLE PRODUCED ERROR CODE, BEING DELETED:")
        print(f"state: {particle.state}")
        print(f"id: {particle.id}")
        print(f"lon: {particle.lon}")
        print(f"lat: {particle.lat}")
        print(f"age: {particle.age}")
        print(f"time: {particle.time}")
        print(f"depth: {particle.depth}")
        print("--------------------------------------------")
        '''
        particle.delete()        


# Now we're kicking every particle, even those flagged as out of bounds after advection.  We are considering the kick as part of the real circulation,
# and we only check for landmask stranding after ALL circulation elements have been added to the d's (particle_dlat, etc).
def AgeAndTidalKick(particle, fieldset, time):
    
    # First, prescribe max lifespan <particle_lifetime_days>, and check particle age against it.  Skip the rest of the kernel if <particle_lifetime_days> has been reached
    particle_lifetime_days = 180
    process_flag = True
    particle.age += particle.dt / 3600  #Hours
    if particle.age > particle_lifetime_days * 24:
        process_flag = False
        particle.delete()

    if process_flag: 
        # Set all particles to an active state ("Evaluate"), kick them, let the internal status check handle re-flagging them as out of bounds as necessary
        if particle.state == StatusCode.ErrorOutOfBounds:
            particle.state = StatusCode.Evaluate
        
        # Interpolating fields will produce a RuntimeError if a particle is outside of the domain 
        # (in which case exit the kernel and let the particle be re-flagged as out of bounds by the internal Parcels status check kernel which we believe executes between every element of the user-provided kernel list)
        # NEW NoTE: Chris wanted the bottom depth to be queried at the previous location, not the "current" one (ie not post-advetion, so not including the d's).  In this case, the try clause previously used is likely unecessary
        #try:
        bottom_depth = -fieldset.H[0, 0 ,particle.lat, particle.lon, particle]
        #except(RuntimeError):
        #    pass
        #else:

        # Set an e-folding scale for the kick magnitude
        tidal_kick_depth_e_folding_scale = 100

        dlon = 0
        dlat = 0

        # Only apply kick if within <cutoff_factor> multiples of <tidal_kick_depth_e_folding_scale>
        cutoff_factor = 4
        if math.fabs(bottom_depth) < cutoff_factor * tidal_kick_depth_e_folding_scale:

            tidal_kick_distance_std = 2500 # Hardcoded prescribed standard devation of kick distance, based on grid cell size (which is ~3km for WCR30, so MUST adjust according to grid being used)
            earth_radius = 6378137
            kick_distance = parcels.ParcelsRandom.normalvariate(0.0, tidal_kick_distance_std) / math.exp( math.fabs(bottom_depth) / tidal_kick_depth_e_folding_scale)
            kick_angle = 2 * math.pi * parcels.ParcelsRandom.uniform(0,1)
            dy = math.sin(kick_angle) * kick_distance
            dx = math.cos(kick_angle) * kick_distance
            dlat_rad = dy/earth_radius
            dlon_rad = dx/(earth_radius * math.cos(math.pi * particle.lat/180))
            dlat = dlat_rad * 180/math.pi
            dlon = dlon_rad * 180/math.pi

            ## Do not apply kick if kick would place particle on land or out of bounds (see except)
            #test_lat = particle.lat + particle_dlat + dlat
            #test_lon = particle.lon + particle_dlon + dlon

        particle_dlat += dlat
        particle_dlon += dlon


# Now handling landmask checking in this "final" movement kernel
def DepthAdjustmentAndLandmask(particle, fieldset, time):

    target_depth_high = -1
    bottom_depth_buffer = 2

    # If out of bounds because particle pierced surface/bottom, place back in ocean, and RESET status to "evaluate" (since an oob/error status is unrecoverable without intervention)
    if particle.state == StatusCode.ErrorOutOfBounds:
        try:
            bottom_depth = -fieldset.H[0, 0 ,particle.lat + particle_dlat, particle.lon + particle_dlon, particle]
        # The above interpolation will fail if the particle is laterally out of bounds, in which case we let it die
        except(RuntimeError):
            pass
        else:
            target_depth_low = bottom_depth + bottom_depth_buffer
            
            # Through surface 
            if particle.depth + particle_ddepth > target_depth_high:
                particle_ddepth -=  (particle.depth + particle_ddepth) - target_depth_high

            # Through bottom
            elif particle.depth + particle_ddepth < target_depth_low:
                particle_ddepth -=  (particle.depth + particle_ddepth) - target_depth_low
            
            # Cancel advection in cases where Parcels thinks particle is below bathymetry despite <bottom_depth> disagreeing (we think there's simply a discrepancy somewhere in an internal grid/interpolation)
            else:
                particle_dlon = 0
                particle_dlat = 0
                particle_ddepth = 0
            
            particle.state = StatusCode.Evaluate

    if particle.state != StatusCode.ErrorOutOfBounds:
        try:
            landmask_value = fieldset.landmask[0, 0, particle.lat + particle_dlat, particle.lon + particle_dlon, particle]
        # The above interpolation should not fail, but I'm scared
        except(RuntimeError):
            pass
        else:
            # Cancel movement if the landmask value is 0 or NaN
            if not landmask_value or landmask_value != landmask_value:
                particle_dlat = 0
                particle_dlon = 0
                particle_ddepth = 0






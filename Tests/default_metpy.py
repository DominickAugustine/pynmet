import cartopy
import cartopy.crs as ccrs
from matplotlib.colors import BoundaryNorm
import matplotlib.pyplot as plt
import numpy as np

from metpy.cbook import get_test_data
from metpy.gridding.gridding_functions import (interpolate, remove_nan_observations,
                                               remove_repeat_coordinates)

def basic_map(proj):
    """Make our basic default map for plotting"""
    fig = plt.figure(figsize=(15, 10))
    view = fig.add_axes([0, 0, 1, 1], projection=proj)
    view.set_extent([-120, -70, 20, 50])
    view.add_feature(cartopy.feature.NaturalEarthFeature(category='cultural',
                                                         name='admin_1_states_provinces_lakes',
                                                         scale='50m', facecolor='none'))
    view.add_feature(cartopy.feature.OCEAN)
    view.add_feature(cartopy.feature.COASTLINE)
    view.add_feature(cartopy.feature.BORDERS, linestyle=':')
    return view


def station_test_data(variable_names, proj_from=None, proj_to=None):
    with open('/home/josue/station_data.txt') as f:
        all_data = np.loadtxt(f, skiprows=1, delimiter=',',
                              usecols=(1, 2, 3, 4, 5, 6, 7, 17, 18, 19),
                              dtype=np.dtype([('stid', '3S'), ('lat', 'f'), ('lon', 'f'),
                                              ('slp', 'f'), ('air_temperature', 'f'),
                                              ('cloud_fraction', 'f'), ('dewpoint', 'f'),
                                              ('weather', '16S'),
                                              ('wind_dir', 'f'), ('wind_speed', 'f')]))

    all_stids = [s.decode('ascii') for s in all_data['stid']]

    data = np.concatenate([all_data[all_stids.index(site)].reshape(1, ) for site in all_stids])

    value = data[variable_names]
    lon = data['lon']
    lat = data['lat']

    if proj_from is not None and proj_to is not None:

        try:

            proj_points = proj_to.transform_points(proj_from, lon, lat)
            return proj_points[:, 0], proj_points[:, 1], value

        except Exception as e:

            print(e)
            return None

    return lon, lat, value


from_proj = ccrs.Geodetic()
to_proj = ccrs.AlbersEqualArea(central_longitude=-97.0000, central_latitude=38.0000)

levels = list(range(-20, 20, 1))
cmap = plt.get_cmap('magma')
norm = BoundaryNorm(levels, ncolors=cmap.N, clip=True)

x, y, temp = station_test_data('air_temperature', from_proj, to_proj)

x, y, temp = remove_nan_observations(x, y, temp)
x, y, temp = remove_repeat_coordinates(x, y, temp)

gx, gy, img = interpolate(x, y, temp, interp_type='linear', hres=75000)
img = np.ma.masked_where(np.isnan(img), img)
view = basic_map(to_proj)
mmb = view.pcolormesh(gx, gy, img, cmap=cmap, norm=norm)
plt.colorbar(mmb, shrink=.4, pad=0, boundaries=levels)
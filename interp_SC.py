import numpy as np
import xarray as xr
from sys import argv
import matplotlib.pyplot as plt
from sol import seaoverland
import intake



cat = intake.open_catalog('catalog.yaml')
print(list(cat))
exit()
fileIn = argv[1]
msk = argv[2]
outname = argv[3]


def main():
    '''
    :return:
    '''
    # this dict associates filename to variable. This is not if filename is RFLV. The variable name are set in the for loop below
    variables = {}
    variables["ASLV"] = 'zos'
    variables["TEMP"] = 'thetao'
    variables["PSAL"] = 'so'
    variables["RFVL"] = 'cur'




    # outname = f'prova_{area}_{variable}.nc'

    filetype = getFileType(fileIn)

    variable = variables[filetype]

    ds_in = xr.open_dataset(fileIn)
    print (ds_in)
    ds_msk = xr.open_dataset(msk)

    if filetype in ['TEMP', 'PSAL']:
        print (f"{filetype} interpolation")
        buffer = []
        for i, depth in enumerate(ds_in.depth):
            print (f'interp lev {i}')
            data = ds_in.isel(depth=i, time=0)
            var=data[variable]
            var.values[var.values > 1000] = np.nan

            # plt.imshow(var, origin='bottom')
            # plt.show()
            # plt.close()
            sol = seaoverland(np.ma.masked_array(var.values, mask=np.isnan(var.values)), iterations=20)
            var.values = sol.filled(fill_value=np.nan)

            lin = var.interp(latitude=ds_msk.lat, longitude=ds_msk.lon, method='linear')
            lin = lin.drop('latitude')
            lin = lin.drop('longitude')

            # plt.imshow(lin, origin='bottom')
            # plt.show()
            # plt.close()
            # exit()
            #sol_lev = seaoverland(np.ma.masked_array(lin.values, mask=np.isnan(lin.values)), iterations=1)
            buffer.append(lin)
        concat_lins = xr.concat(buffer, dim='depth')
        depths = ds_msk.depth.values
        ds_vertInterp = concat_lins.interp(depth=depths, method='linear')

        concat_lins.values[concat_lins.values > 1000] = np.nan

        for i, depth in enumerate(depths):
            print (i, depth)
            msk = ds_msk.mask.isel(depth=i).values

            # plt.imshow(msk,origin='bottom')
            # plt.title(depth)
            # plt.savefig(f'/Users/scausio/Dropbox (CMCC)/PycharmProjects/chinese_interpolation/rita_20210714/data/plts/{depth}.png')
            # plt.close()

            tomask = ds_vertInterp.isel(depth=i).values
            tomask[msk != 1] = np.nan
            plt.imshow(tomask,origin='bottom')
            plt.title(depth)
            plt.savefig(f'/Users/scausio/Dropbox (CMCC)/PycharmProjects/chinese_interpolation/rita_20210714/data/plts/tomaskGLORS{depth}.png')
            plt.close()

            ds_vertInterp.sel(depth=depth).values = tomask

        data_newcoord = ds_vertInterp.assign_coords(time=ds_vertInterp.time)
        data_newcoord.values[data_newcoord.values > 1000] = np.nan
        data_newcoord = data_newcoord.fillna(value=1.e20)
        data_newcoord.attrs['_FillValue'] = 1.e20
        expanded = data_newcoord.expand_dims('time')

    elif filetype == 'RFVL':
        print ("currents interpolation")
        currents_buffer = []
        for variable in ['uo', 'vo']:
            buffer = []
            print (variable)
            for i, depth in enumerate(ds_in.depth):
                print (f'interp lev {i}')
                data = ds_in.isel(depth=i, time=0)
                var = data[variable]
                var.values[var.values > 1000] = np.nan
                sol = seaoverland(np.ma.masked_array(var.values, mask=np.isnan(var.values)), iterations=20)
                var.values = sol.filled(fill_value=np.nan)

                lin = var.interp(latitude=ds_msk.lat, longitude=ds_msk.lon, method='linear')
                lin = lin.drop('latitude')
                lin = lin.drop('longitude')

                buffer.append(lin)

            concat_lins = xr.concat(buffer, dim='depth')
            depths = ds_msk.depth.values
            ds_vertInterp = concat_lins.interp(depth=depths, method='linear')

            concat_lins.values[concat_lins.values > 1000] = np.nan
            for i, depth in enumerate(depths):
                print (i, depth)
                msk = ds_msk.mask.isel(depth=i).values

                tomask = ds_vertInterp.isel(depth=i).values

                tomask[msk != 1] = np.nan
                ds_vertInterp.sel(depth=depth).values = tomask

            data_newcoord = ds_vertInterp.assign_coords(time=ds_vertInterp.time)
            data_newcoord.values[data_newcoord.values > 1000] = np.nan
            data_newcoord = data_newcoord.fillna(value=1.e20)
            data_newcoord.attrs['_FillValue'] = 1.e20
            expanded = data_newcoord.expand_dims('time')
            currents_buffer.append(expanded)

        expanded = xr.merge(currents_buffer)



    elif filetype == 'ASLV':
        print ("sea level interpolation")
        print (f'interp lev 0')
        data = ds_in.isel(time=0)
        print (data)
        var = data[variable]
        var.values[var.values > 1000] = np.nan
        sol = seaoverland(np.ma.masked_array(var.values, mask=np.isnan(var.values)), iterations=20)
        var.values = sol.filled(fill_value=np.nan)

        lin = var.interp(latitude=ds_msk.lat, longitude=ds_msk.lon, method='linear')
        lin = lin.drop('latitude')
        lin = lin.drop('longitude')

        msk = ds_msk.mask.isel(depth=0).values

        tomask = lin.values

        tomask[msk != 1] = np.nan
        lin.values = tomask
        lin.values[lin.values > 1000] = np.nan
        lin = lin.fillna(value=1.e20)
        lin.attrs['_FillValue'] = 1.e20

        expanded = lin

    # Here you can set the box for the Black Sea
    minLon = 27
    minLat = 40
    maxLon = 42
    maxLat = 48

    expanded = expanded.where(np.logical_not(
        (expanded.lat > minLat) & (expanded.lat < maxLat) & (expanded.lon > minLon) & (expanded.lon < maxLon)),1.e20)
    expanded.to_netcdf(outname)

if __name__ == '__main__':
    main()

#!/usr/bin/env python

import xarray as xr
import numpy as np
from utils import getConfiguration
from sol import seaoverland
from argparse import ArgumentParser
import matplotlib.pyplot as plt


def maskLand(tobemasked, target, cat_in,cat_out):
    if len(cat_out.coords)==3:
        depths=target[cat_out.coords.depth].values

        for depth in depths:
            print(f'depth {depth}')
            level_msk = target[cat_out.variables.lsm].sel(depth=depth).values
            print (level_msk.shape)
            tomask = tobemasked.sel(depth=depth).values
            print(tomask.shape)
            tomask[level_msk != 1] = np.nan
            tobemasked.sel(depth=depth).values = tomask
    else:
        level_msk = target[cat_out.variables.lsm].isel(depth=0).values
        tobemasked.values[level_msk != 1] = np.nan
    tobemasked.values[tobemasked.values == np.nan] = cat_in.fillvalue
    return tobemasked

def _checkVarOrder(ds,coords,cat_in):
    if len(coords)==2:
        return ds.transpose(cat_in.coords.time,cat_in.coords.depth,cat_in.coords.latitude,cat_in.coords.longitude)
    elif len(coords)==1:
        try:
            return ds.transpose(cat_in.coords.time, cat_in.coords.latitude,
                                cat_in.coords.longitude)
        except:
            return ds.transpose(cat_in.coords.depth, cat_in.coords.latitude,
                         cat_in.coords.longitude)
    else:
        return ds.transpose(cat_in.coords.latitude,
                            cat_in.coords.longitude)

def set_DS_horiz_regrid(source, target, cat_in, cat_out):
    outDS = target.copy(deep=True)
    # this is needed to copy the horizontal grid
    if cat_out.coords.depth in list(target._coord_names):
        outDS = outDS.isel({cat_out.coords.depth: 0})
        outDS=outDS.drop(cat_out.coords.depth )

    # add the same time variable as in the input file
    if cat_in.coords.time in list(source._coord_names):
        outDS[cat_in.coords.time] = source[cat_in.coords.time]
    # add the same depth variable as in the input file
    if cat_in.coords.depth in list(source._coord_names):
        outDS[cat_in.coords.depth] = source[cat_in.coords.depth]
    return outDS.drop(cat_out.variables.lsm)

def set_DS_vertical_regrid(source, target, cat_in, cat_out):
    outDS = target.copy(deep=True)
    if cat_out.coords.depth in list(target._coord_names):
        outDS = outDS.isel({cat_out.coords.depth: 0})
        outDS=outDS.drop(cat_out.coords.depth )

        # add the same time variable as in the input file
        if cat_in.coords.time in list(source._coord_names):
            outDS[cat_in.coords.time] = source[cat_in.coords.time]

        return outDS.drop(cat_out.variables.lsm)
    else:
        return


def subsampleDepth(source, target,cat_in,cat_out):
    try:
        target[cat_in.coords.depth]

        imin = np.argmin(np.abs(source[cat_in.coords.depth].values - np.nanmin(target[cat_out.coords.depth].values)))

        if imin == 0:
            pass
        else:
            imin -= 1

        imax = np.argmin(np.abs(source[cat_in.coords.depth].values - np.nanmax(target[cat_out.coords.depth].values)))
        if imax == len(source[cat_in.coords.depth].values) - 1:
            pass
        else:
            imax += 1
        return source.isel(depth=np.arange(imin, imax + 1, 1))
    except:
        return source.isel(depth=0)


def horizontal_regrid(data_2D, output_grid, cat):

    data_2D.values[data_2D.values == cat.fillvalue] = np.nan  # data_2D.where()
    # apply seaoverland
    sol = seaoverland(np.ma.masked_array(data_2D.values, mask=np.isnan(data_2D.values)), iterations=10).filled(
        fill_value=np.nan)
    # sol_source[cat.variables[variable]].sel({cat.coords.depth:d_val, cat.coords.time:t_val}).values= sol.filled(fill_value=np.nan)
    data_2D.values = sol
    # horizontal regrid
    linear_interpolated = data_2D.interp(
        {cat.coords.latitude: output_grid[cat.coords.latitude], cat.coords.longitude: output_grid[cat.coords.longitude]},
        method='linear')
    return linear_interpolated


def main():
    # parser = ArgumentParser(description='Interpolate model results')
    # parser.add_argument('-c', '--catalog', default='catalog.yaml', help='catalog file')
    # parser.add_argument('-n', '--name', required=True, help='dataset name (in catalog)')
    # parser.add_argument('-i', '--input', required=True, help='input file')
    # parser.add_argument('-o', '--output', required=True, help='output file')
    #
    # args = parser.parse_args()

    source = xr.open_dataset(input_file)
    target = xr.open_dataset(out_file)

    # opening catalog
    cat_in = getConfiguration('catalog.yaml')['input_file']
    cat_out = getConfiguration('catalog.yaml')['output_grid']
    print(source)
    #

    # this checks 3 and 4 dimension
    coords = list(source._coord_names)
    coords.remove(cat_in.coords.longitude)
    coords.remove(cat_in.coords.latitude)

    source = _checkVarOrder(source, coords,cat_in)

    # subsample input according depth range of output grid
    source = subsampleDepth(source, target,cat_in,cat_out)

    variable_buffer = []
    for variable in cat_in.variables:
        print(cat_in.variables[variable])
        var_data = source[cat_in.variables[variable]]
        print(f'Horizontal intepolation for  {variable}')
        # set dataset for horizontal regrid
        hor_interp_ds = set_DS_horiz_regrid(source, target, cat_in, cat_out)
        print (hor_interp_ds)
        if len(cat_in.coords) == 4:
            hor_interp_ds[variable] = (
            [cat_in.coords.time, cat_in.coords.depth, cat_out.coords.latitude, cat_out.coords.longitude], np.zeros((len(
                hor_interp_ds[cat_in.coords.time]), len(hor_interp_ds[cat_in.coords.depth]), len(
                hor_interp_ds[cat_out.coords.latitude]), len(hor_interp_ds[cat_out.coords.longitude]))))

            for t_index, t_val in enumerate(var_data[cat_in.coords.time]):
                print(f'Time {t_val.values}')
                for d_index, d_val in enumerate(var_data[cat_in.coords.depth]):
                    data_2D = var_data.sel({cat_in.coords.depth: d_val, cat_in.coords.time: t_val})
                    linear_interpolated = horizontal_regrid(data_2D, hor_interp_ds, cat_in)
                    hor_interp_ds[variable].values[t_index][d_index] = linear_interpolated.values
                    # plt.imshow(hor_interp_ds[variable].sel({cat_in.coords.depth: d_val, cat_in.coords.time: t_val}).values)
                    # plt.show()
        elif len(cat_in.coords) == 3:
            try:
                hor_interp_ds[variable] = (
                    [cat_in.coords.time, cat_out.coords.latitude, cat_out.coords.longitude], np.zeros((len(
                        hor_interp_ds[cat_in.coords.time]), len(hor_interp_ds[cat_out.coords.latitude]), len(
                        hor_interp_ds[cat_out.coords.longitude]))))
                for t_index, t_val in enumerate(var_data[cat_in.coords.time]):
                    data_2D = var_data.sel({cat_in.coords.time: t_val})
                    linear_interpolated = horizontal_regrid(data_2D, hor_interp_ds, cat_in)
                    hor_interp_ds[variable].values[t_index] = linear_interpolated
            except:
                hor_interp_ds[variable] = (
                    [cat_in.coords.depth, cat_out.coords.latitude, cat_out.coords.longitude],
                    np.zeros((len(hor_interp_ds[cat_in.coords.depth]), len(hor_interp_ds[cat_out.coords.latitude]), len(
                        hor_interp_ds[cat_out.coords.longitude]))))
                for d_index, d_val in enumerate(var_data[cat_in.coords.depth]):
                    data_2D = var_data.sel({cat_in.coords.depth: d_val})
                    linear_interpolated = horizontal_regrid(data_2D, hor_interp_ds, cat_in)
                    hor_interp_ds[variable].values[d_index] = linear_interpolated
        elif len(cat_in.coords) == 2:
            hor_interp_ds[variable] = (
                [cat_out.coords.latitude, cat_out.coords.longitude],
                np.zeros((len(hor_interp_ds[cat_in.coords.depth]), len(hor_interp_ds[cat_out.coords.latitude]), len(
                    hor_interp_ds[cat_out.coords.longitude]))))

            linear_interpolated = horizontal_regrid(var_data, hor_interp_ds, cat_in)
            hor_interp_ds[variable].values = linear_interpolated

        if len(cat_out.coords) == 3:
            print(f'Vertical intepolation for  {variable}')
            depths = target[cat_out.coords.depth].values
            output_ds = hor_interp_ds.interp(depth=depths, method='linear')
        else:
            output_ds = hor_interp_ds

        print(f'Applying land-mask for  {variable}')
        if cat_in.coords.time in list(output_ds._coord_names):
            for i, t in enumerate(output_ds.time):
                output_ds[variable].values[i] = maskLand(output_ds[variable].isel({cat_in.coords.time: i}), target,
                                                         cat_in, cat_out)
        else:
            output_ds[variable].values = maskLand(output_ds[variable], target, cat_in, cat_out)

        variable_buffer.append(output_ds)
        print (f'variable {variable} completed')
    print (f'Saving output to {outname}.nc')
    xr.merge(variable_buffer).to_netcdf(f'{outname}.nc')


input_file='tests/20040101_d-MERCATOR--TEMP-GREPv2-NWP-b20210519_re-sv01.00.nc'
out_file='tests/test_mask.nc'
outname='prova'


if __name__ == '__main__':
    main()







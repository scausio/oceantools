<h1>Oceantools</h1>

Collection of tools for oceanography

<h2>How to install</h2>

The tool is  written in Python3, the use of a virtual environment is suggested.


<p>In the oceantools/install you can find the yaml file to build a new environment:</p>
<ul>
```
<li>cd oceantools/install</li>
<li>conda env create -f environment.yml</li>
```
</ul>

!Please be sure that anaconda in installed under your machine!

<p>Activate the virtual envirnonment:</p>
<ul>
```
<li>conda activate oceantools</li>
```
</ul>


<h2>How to run spatial regridding for regular netcdf files</h2>
<em>spatial_regrid.py</em> performs horizontal and vertical bilinear interpolation of regular netcdf file, from an input file to a target user-defined grid. The procedure includes also a Sea-Over-Land step before regridding.

<p>The command is:</p>
<ul>
```
<li>cd oceantools/geometry</li>
<li>python spatial_regrid.py -i \<input_file\> -o \<output_grid\> -n <\output filename\> </li>
```
</ul>


<strong>input_file</strong> is the absolute path to the file you want to regrid. The file needs to have 1D spatial coordinates (as in CF-compliant netcdf). The tool is not able to manage 2D coordinates (e.g NEMO based files).
The netcdf can have also dimensions for time and or depth.

<strong>output_grid</strong> the target grid should can (or not) have a vertical dimension. If the vertical dimension is not present, the interpolation will be performed only at the first layer of the input_file
If a vertical dimension is present in the target grid, the data will be interpolated also in vertical.

<strong>output filename</strong> name for the output netcdf


The user should provides also some information about the name for dimensions and variable using the <em>catalog.yaml</em> file.

here an example:


> -------- catalog.yaml file --------\n
> source:\n
>  input_file:\n
>    fillvalue: 1e20\n
>    coords:\n
>      latitude: lat\n
>      longitude: lon\n
>      depth: depth\n
>      time: time\n
>    variables:\n
>      temperature: thetao\n
>      #salinity: so\n
>  output_grid:\n
>    coords:\n
>      latitude: lat\n
>      longitude: lon\n
>      depth: depth\n
>    variables:\n
>        lsm: mask\n
>----------------------------------------\n
>
> **#** is the comment character in catalog.\n
>



<p>input_file block allows to define:</p>
<ul>
<li> what is the fill values of the input file</li>
<li> in the coords block, what are the latitude and longitude names.
 If the input file has also time and/or depth dimensions these must be declared here. If not, the procedure raise a self-explaining error.
 If the  input_file has more times, the regridding will be applied at each time.
Only four names allowed in the coords block: latitude, longitude, time, depth</li>
<li> in the variables block, what is/are the variable/s to regrid. Here the user can define one of more variables, and the keys used in the block (temperature and salinity in the example) will be used as variable name in the output file
</ul>

<p>output_grid block allows to define:</p>
<ul>
<li>in the coords block, what are the latitude and longitude names. If the output_grid has also vertical coordinate, this has to be defined here.
 If the vertical coordinate is not defined here, (using depth key in catalog) the regrid will be applied only at the first level of the input_file.</li>
<li>in the variables block the user defines the name of the land-sea mask variable. The  mask should has been defined as following: ocean=1 (or True), land=0 (or False)</li>
</ul>

In tests folder some example netcdf  are available, with/without time and depth dimensions, with one or two variables.

examples of run test:

./spatial_regrid.py  -i ../tests/NWP_noTime.nc -o ../tests/mask.nc -n example_1  ---> for emperature horizontal and vertical regrid without time dimension
./spatial_regrid.py  -i ../tests/NWP_2vars.nc -o ../tests/mask.nc -n example_2 ---> for salinity and temperature horizontal and vertical regrid
./spatial_regrid.py  -i ../tests/NWP_complete.nc -o ../tests/mask.nc -n example_3 ---> temperature horizontal and vertical regrid with time dimension
./spatial_regrid.py  -i ../tests/NWP_complete.nc -o ../tests/mask_surf.nc -n example_3 ---> temperature horizontal  regrid with time dimension only at surface
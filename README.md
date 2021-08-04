<h1>Oceantools</h1>

Collection of tools for oceanography

<h2>How to install</h2>

The tool is  written in Python3, the use of a virtual environment is suggested.


<p>In the oceantools/install you can find the yaml file to build a new environment:</p>
<ul>
<li><em>cd oceantools/install</em></li>
<li><em>conda env create -f environment.yml</em></li>
</ul>

<strong>Please be sure that anaconda is installed under your machine!  </strong>

<p>Activate the virtual environment:</p>
<ul>
<li><em>conda activate oceantools</em></li>
</ul>


<h2>How to run spatial regridding for regular netcdf files</h2>
<em>spatial_regrid.py</em> performs horizontal and vertical bilinear interpolation of regular netcdf file, from an input file to a target user-defined grid. The procedure includes also a Sea-Over-Land step before regridding.

<p>The command is:</p>
<ul>
<li><em>cd oceantools/geometry</em></li>
<li><em>python spatial_regrid.py -i <strong>input_file</strong> -o <strong>output_grid</strong> -n <strong>output filename</strong> </em></li>
</ul>


<strong>input_file</strong> is the absolute path to the file you want to regrid. The file needs to have 1D spatial coordinates (as in CF-compliant netcdf). The tool is not able to manage 2D coordinates (e.g NEMO based files).

<strong>output_grid</strong> is the target grid which can (or not) have a vertical dimension. If the vertical dimension is not present, the interpolation will be performed only at the first layer of the input_file .
If a vertical dimension is present in the target grid, the data will be interpolated also in vertical.

<strong>output filename</strong> name for the output netcdf


The user should provides also some information about the name for dimensions and variable using the <em>catalog.yaml</em> file.

Here an example:


> -------- catalog.yaml file --------
> source:
> <ul>
>
>  input_file:
>  <ul>
>  fillvalue: 1e20
>
>   coords:
>    <ul>
>
>      latitude: lat
>
>      longitude: lon
>
>      depth: depth
>
>      time: time
>
>   </ul>
>    variables:
>    <ul>
>
>      temperature: thetao
>      #salinity: so
>    </ul>
>    </ul>
>  output_grid:
>
>  <ul>
>    coords:
>   <ul>
>
>      latitude: lat
>      longitude: lon
>      depth: depth
>    </ul>
>    variables:
>    <ul>
>
>        lsm: mask
>
>    </ul>
>
> </ul>
>----------------------------------------

>
> **#** is the comment character in catalog.
>



<p><strong>input_file block</strong> allows to define:</p>
<ul>
<li>  fill values of the input file</li>
<li> in the <strong>coords block</strong>,  the latitude and longitude names.
 If the <em>input_file</em> has also time and/or depth dimensions these must be declared here. If not, the procedure raise a self-explaining error.
 If the  <em>input_file</em> has time dimension, the regridding will be applied at each time.
<strong>!!!Only four names allowed in the coords block: latitude, longitude, time, depth!!!</strong></li>
<li> in the <strong>variables block</strong>, the variable/s to regrid. Here the user can define one or more variables, and the keys used in the block (temperature and salinity in the example) will be used as variable name in the output file.
</ul>

<p><strong>output_grid block</strong> allows to define:</p>
<ul>
<li>in the <strong>coords block</strong>, what are the latitude and longitude names. If the <em>output_grid</em> has also vertical coordinate, this has to be defined here.
 If the vertical coordinate is not defined here, (using depth key in catalog) the regrid will be applied only at the first level of the <em>input_file</em>.</li>
<li>in the <strong>variables block</strong> the user defines the name of the land-sea mask variable. The  mask should has been defined as following: <em>ocean=1 (or True), land=0 (or False)</em></li>
</ul>

<h2>Test </h2>
In _<em>oceantools/geometry/tests</em> directory some example netcdf  are available, with/without time and depth dimensions, with one or two variables.

<p>Examples of test commands: </p>
 <ul>
<li>python ./spatial_regrid.py  -i ../tests/NWP_noTime.nc -o ../tests/mask.nc -n example_1  ---> for temperature horizontal and vertical regrid without time dimension  </li>
<li>python ./spatial_regrid.py  -i ../tests/NWP_2vars.nc -o ../tests/mask.nc -n example_2 ---> for salinity and temperature horizontal and vertical regrid  </li>
<li>python ./spatial_regrid.py  -i ../tests/NWP_complete.nc -o ../tests/mask.nc -n example_3 ---> temperature horizontal and vertical regrid with time dimension</li>

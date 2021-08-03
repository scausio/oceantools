import numpy as np


def seaoverland(data, iterations=1, copy=False):
    """
    Python implementation of G. Girardi's seaoverland.f90.
    author: E.Jansen
    Extends grids defined only at sea onto the land such that bilinear
    interpolation of the grid is also possible close to the coastline. The
    procedure determines the value of an undefined grid point by averaging the
    defined neighbour points among the 8 closest neighbours. Every iteration
    therefore extends the grid with one additional row of points towards the
    coastline.

    With copy set to True a copy of the data is returned leaving the original
    untouched. Otherwise the data is modified in place and returned.

    Parameters
    ----------
    data : numpy.ma.masked_array
        Grid (2 dimensions) to be extrapolated.
    iterations : int, optional, default: 1
        Number of iterations (i.e. extent of extrapolation).
    copy : boolean, optional, default: False
        Create a copy of data instead of modifying it in place.
    """
    if copy:
        data = np.ma.copy(data)

    if not isinstance(data, np.ma.masked_array) or not data.mask.any():
        return data

    for _ in range(iterations):
        shifted = []
        ni, nj = data.shape
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i != 0 or j != 0:
                    # Shift the grid by i horizontally and j vertically and
                    # append it to the array. Shifted grids are 2 units smaller
                    # in both dimensions to accomodate the shift.
                    shifted.append(data[1 + i:ni - 1 + i, 1 + j:nj - 1 + j])

        # Calculate the mean value of the shifted grids to obtain the
        # approximated values. Only non-masked entries are taken into account.
        approx = np.ma.mean(shifted, axis=0)

        # Create a view without the outer points (so it is the same size as the
        # shifted grids), then copy the approximated values for the cells that
        # are masked.
        view = data[1:-1, 1:-1]
        np.copyto(view, approx, where=(view.mask & ~approx.mask))

        # Combine the two masks, unmasking values that were masked in view but
        # have been successfully approximated.
        view.mask &= approx.mask
    return data
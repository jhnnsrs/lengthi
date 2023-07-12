from arkitekt import register, log
from mikro.api.schema import ROIFragment, RepresentationFragment, ROIType, from_xarray
from scipy import interpolate
from scipy.spatial.distance import euclidean
from scipy import interpolate
import scipy
import numpy as np
from typing import Optional
import xarray as xr


@register()
def straighten(roi: ROIFragment, height: int = 10, num_points: Optional[int] = None) -> RepresentationFragment:
    """Straigten a ROI.
    
    Straigtens a ROI by fitting a spline to the ROI and then sampling the image
    along the spline.
    
    Args:
        roi (ROIFragment): The ROI to be straigtened.
        height (int): The width of the straightened ROI.
        num_points (int): The number of points to interpolate along the spline.

    """
    assert roi.type == ROIType.PATH, "ROI must be a path"

    image = roi.representation.data.sel(z=0, t=0, c=0).compute()

    plist = roi.get_vector_data(dims="yx")

    # We need to clean possible consecutive duplicates
    mask = np.insert(np.any(np.diff(plist, axis=0), axis=1), 0, True) # Checkin if the difference between two consecutive points is zero
    plist = plist[mask]

    if num_points is None:
        # Calculate the length of the path
        path_length = sum(euclidean(plist[i], plist[i+1]) * 2 for i in range(len(plist)-1))
        # Determine the appropriate number of points to interpolate
        num_points = int(path_length * 1)

    print(num_points)
    log(num_points)
    ctr =np.array(plist)

    x=ctr[:,0]
    y=ctr[:,1]
    print(x)
    print(y)

    tck, u= interpolate.splprep([x,y],k=3,s=0)
    u=np.linspace(0,1,num=num_points,endpoint=True)
    out = interpolate.splev(u,tck)
    scaling = np.diff(u)[0]
    p_x, p_y = out

    # Compute the derivatives
    der = interpolate.splev(u, tck, der=1)
    dx_i, dy_i = der

    # Compute the differential arc lengths
    ds = np.sqrt(dx_i**2 + dy_i**2) * np.diff(u)[0]

    # Sum up the differential arc lengths to get the total arc length
    arc_length = np.sum(ds)
    log(f"The arc length of the spline is {arc_length}.")




    # Discretize points along the spline (fitting it to points along the spline, that are one pixel apart)
    running_length = 0
    pixels = []
    width = 0

    for x, y, dx, dy, in zip(p_x, p_y, dx_i, dy_i):

        length = np.sqrt(dx**2 + dy**2) * scaling
        running_length += length

        if running_length > 1:
            width += 1

            stepx, stepy = -dy, dx

            for i in range(height):
                t1 = [x  + stepx * (i - height//2) * scaling, y + stepy * (i - height//2) * scaling]
                pixels.append(t1)

    # Points is transponsed to be in the correct format for map_coordinates
    points = np.array(pixels).T
    values = scipy.ndimage.map_coordinates(image, points, order=1)
    straightened_image = values.reshape((width, height))
    straightened_image = xr.DataArray(straightened_image, dims=("x", "y"))
    return from_xarray(straightened_image, origins=[roi.representation.id], roi_origins=[roi.id], name=f"Straightened {roi.representation.id} along {roi.label}")



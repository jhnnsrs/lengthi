# lengthi

This is a simple programm to straighten out an image given a path of points.
(Part of the Arkitekt platform). It utilizes spline interpolation to create a
smooth path between the points, and then interpolates values from the image
along the path AND its perpendicular sourroundings. (Just like a tube around
the path). Right now the implementation is two-dimensional, but it should be
fairly easy to extend it to three dimensions.

For ImageJ folks: Similar to "Straighten..." plugin, but enabled in python
and for the arkitekt platform.
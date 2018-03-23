Divebomb
========
Divebomb is a python package that uses pandas to divide a timeseries of depths into individual dives.

Each dive is then profiled with the following attributes:

- **max_depth** - the max depth in the dive
- **dive_start** - the timestamp of the first point in the dive
- **dive_end** - the timestamp of the last point in the dive
- **bottom_start** - the timestamp of the first point in the dive when the animal is at depth
- **td_bottom_duration** - a timedelta object containing the duration of the time the animal is at depth in seconds
- **td_descent_duration** - a timedelta object containing the duration of the time the animal is descending in seconds
- **td_ascent_duration** - a timedelta object containing the duration of the time the animal is ascending in seconds
- **td_surface_duration** - a timedelta object containing the duration of the time the animal is at the surface in seconds
- **bottom_variance** - the variance of the depth while the animal is at the bottom of the dive
- **dive_variance** - the variance of the depth for the entire dive.
- **descent_velocity** - the average velocity of the descent
- **ascent_velocity** - the average velocity of the descent
- **peaks** - the number of peaks found in the dive profile
- **left_skew** - a boolean of 1 or 0 indicating if the dive is left skewed
- **right_skew** - a boolean of 1 or 0 indicating if the dive is right skewed
- **no_skew** - a boolean of 1 or 0 indicating if the dive is not skewed

The dive profiles are reduced to 8 dimensions using Principal Component Analsysis. Guassian Mixed Models are generated using theses variables
and the minimal Bayesian Information Criterion is used to determine the optimal number of clusters. The dives are split into the clutsers using
Agglomerative Hierarchical Clustering (from sklearn). The dives are then display through iPython notebooks or saved to netCDF files organized by cluster.


Surfacing Events
----------------
Surface events are not separated out, but instead left to the user to determine if a cluster should classified as durface events.
Surfacing times are those to be above the surface threshold, which is determined by the following equation:
:math:`animal length * cos(45 radians)`

To get the surface times/events only you can subtract the surface duration from the end of the dive. You’ll then have the start
time for the surface event of the dive.


Acceleration Thresholds
-----------------------
The start of each dive is determined by a downward shift of at least 0.015 m/s :sup:`2`. This can be adjusted by setting the
``acceleration_threshold`` argument in the main function. There is occasionally overlap of a point or two between dives to make
sure the entire dive is encapsulated on its own.


Timestamps
----------
The input timestamps are expected to be in a datetime format. The output timestamps are in ``seconds since 1970-01-01``.
Every netCDF file has the time unit saved as an attribute as a reminder. All dive attributes that start with ``td_`` are
a duration in seconds. The ``time``, ``dive_start``, ``dive_end``, and ``bottom_start`` will use the units mentioned above.
the netCDF4 library has a ``num2date`` function that will convert the values back to a datetime object.

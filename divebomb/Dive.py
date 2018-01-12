from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import plotly.offline as py
import plotly.graph_objs as go
import copy
import sys
from divebomb.DiveShape import DiveShape

from netCDF4 import Dataset, num2date, date2num
import peakutils as pk

units = 'seconds since 1970-01-01'


class Dive:
    def __init__(self, data, columns={'depth': 'depth', 'time': 'time'}, surface_threshold=3.0, suppress_warning=False):
        """
        :param data: the time and depth values for the dive
        :param surface_threshold: minmum depth to constitute a dive
        :param supress_warning: indicator to ignore dives dives with little data

        """

        self.sufficient=True
        if data[columns['time']].dtypes != np.float64:
            data.time = num2date(data.time.tolist(),units=units)

        self.data = data.sort_values('time').reset_index(drop=True)
        self.surface_threshold = surface_threshold

        for k, v in columns.items():
            if k != v:
                self.data[k] = self.data[v]
                self.data.drop(v, axis=1)
        self.max_depth = self.data.depth.max()
        self.dive_start = self.data.time.min()
        self.bottom_start = None
        self.td_bottom_duration = None
        self.bottom_difference = None
        try:
            self.td_descent_duration = self.get_descent_duration()
            self.td_ascent_duration = self.get_ascent_duration()
            self.td_surface_duration = self.get_surface_duration()
            self.bottom_variance = self.set_bottom_variance()
            self.descent_velocity = self.get_descent_velocity()
            self.ascent_velocity = self.get_ascent_velocity()
            self.total_duration = self.td_ascent_duration+self.td_bottom_duration+self.td_descent_duration+self.td_surface_duration
            self.dive_duration = self.total_duration - self.td_surface_duration
            self.dive_end = self.dive_start + self.total_duration
            self.no_skew = 0
            self.right_skew = 0
            self.left_skew = 0
            self.set_skew()
            self.peaks = self.get_peaks()

        except Exception:
            self.sufficient=False
            if self.data.depth.max() <= surface_threshold:
                self.td_descent_duration = None
                self.td_ascent_duration = None
                self.td_surface_duration = None
                self.bottom_variance = None
                self.dive_variance = None
                self.descent_velocity = None
                self.ascent_velocity = None
            else:
                if not suppress_warning:
                    print("Warning: There is not enough information for this dive.\n"+str(self.data.time.min() )+ " to "+str(self.data.time.max()))

    # Calculate and set the descent duration.
    # Iterates through the start of the dive looking for a change in the standard deviation.
    # Once the change is found the descent duration is calculated using that point.
    def get_descent_duration(self):
        """
        :return: the descent duration in seconds
        """
        std_dev = 0
        for i, r in self.data.iterrows():
            next_std_dev = np.std(self.data.loc[:i, 'depth'])
            if (next_std_dev <= std_dev or self.data.loc[i, 'depth'] >= self.data.loc[(i + 1), 'depth']) and self.data.loc[i, 'depth'] > (self.max_depth * 0.85):
                self.bottom_start = self.data.loc[i, 'time']
                return (self.data.loc[i, 'time'] - self.data.loc[0, 'time'])
                break
            else:
                std_dev = next_std_dev
        return self.td_descent_duration

    # Calculate and set the ascent duration and bottom duration.
    # Iterates through the end of the dive looking for changes in standard deviation.
    # Once the change is found the ascent duration and bottom duration are set.
    def get_ascent_duration(self):
        """
        This function also sets the bottom duration.

        :return: the ascent duration in seconds
        """
        end_index = -1
        std_dev = 0

        # Find the crest of the dive in reversed values
        for i, r in self.data.sort_values('time', ascending=False).iterrows():
            if self.data.loc[(i - 1), 'depth'] >= self.surface_threshold:
                end_index = i
                break

        # Finds the the change in standard deviation to determine the end of the bottom of the divide.
        for i, r in self.data[:end_index].sort_values('time', ascending=False).iterrows():
            next_std_dev = np.std(self.data.loc[i:end_index, 'depth'])
            if ((next_std_dev < std_dev or self.data.loc[i, 'depth'] >= self.data.loc[(i - 1), 'depth']) and self.data.loc[i, 'depth'] > (self.max_depth * 0.85)) or self.data.loc[i, 'depth'] > (self.max_depth * 0.90):
                self.td_bottom_duration = self.data.loc[i,'time'] - self.bottom_start
                if(end_index > 0):
                    return (self.data.loc[end_index, 'time'] - self.data.loc[i, 'time'])

                break
            else:
                std_dev = next_std_dev
        return self.td_ascent_duration


    # Get the surface duration by subtracting the ascent, descent, and bottom durations.
    def get_surface_duration(self):
        """
        :return: the surface duration in seconds
        """
        duration = self.data.time.max() - self.data.time.min()
        self.td_surface_duration = duration - self.td_descent_duration - self.td_bottom_duration - self.td_ascent_duration
        return self.td_surface_duration

    # Calculate the descent velocity Delta Depth/Delta Time
    def get_descent_velocity(self):
        """
        :return: the descent velocity in m/s
        """
        descent_data = self.data[self.data.time <= self.bottom_start]
        self.descent_velocity = (descent_data.depth.max() - descent_data.depth.min()) / self.td_descent_duration
        return self.descent_velocity

    # Calculate the ascent velocity Delta Depth/Delta Time
    def get_ascent_velocity(self):
        """
        :return: the ascent velocity in m/s
        """
        ascent_data = self.data[self.data.time >= (
            self.bottom_start + self.td_bottom_duration)]
        self.ascent_velocity = (ascent_data.depth.max() - ascent_data.depth.min()) / self.td_ascent_duration
        return self.ascent_velocity

    # Calculate and set the bottom variance
    def set_bottom_variance(self):
        """
        This function also set total dive variance

        :return: the standard variance in depth during the bottom portion of the dive in meters
        """
        dive_data = self.data[(self.data.time >= self.dive_start) & (self.data.time <= (self.bottom_start + self.td_bottom_duration + self.td_ascent_duration))]
        self.dive_variance = np.std(dive_data.depth)
        bottom_data = self.data[(self.data.time >= self.bottom_start) & (self.data.time <= (self.bottom_start + self.td_bottom_duration))]
        self.bottom_variance = np.std(bottom_data.depth)
        self.bottom_difference = bottom_data.depth.max() - bottom_data.depth.min()
        return self.bottom_variance

    # Calculate and set total dive variance
    def set_dive_variance(self):
        """
        :return: the standard variancet in depth during dive in meters
        """
        dive_data = self.data[(self.data.time >= self.dive_start) & (self.data.time <= (self.bottom_start + self.td_bottom_duration + self.td_ascent_duration))]
        self.dive_variance = np.std(dive_data.depth)
        return self.dive_variance

    def set_skew(self):
        """
        :return: a string of either right or left
        """
        if self.td_ascent_duration > self.td_descent_duration:
            self.right_skew = 1
        elif self.td_descent_duration > self.td_ascent_duration:
            self.left_skew = 1
        else:
            self.no_skew = 1

    def get_peaks(self):
        peak_thres = (1 - (self.data.depth.mean() - (self.surface_threshold))/ self.data.depth.max())
        peaks = pk.indexes(self.data.depth*(-1), thres=min([0.2, peak_thres]), min_dist=max((10/self.data.time.diff().mean()),3))
        self.peaks = len(peaks)
        return self.peaks


    # Return the dictionary of the object
    def to_dict(self):
        """

        :return: a dictionary of the dive profile
        """
        dive = copy.deepcopy(self.__dict__)
        del dive['data']
        return dive

    # Used to plot the dive
    def plot(self):

        """

        :return: a plotly graph showing the phases of the dive
        """
        # Set the data to plot the segments of the dive
        if self.sufficient:
            # Get and set the descent data
            descent_data = self.data[self.data.time <= self.bottom_start]
            descent = go.Scatter(
                x=num2date(descent_data.time.tolist(), units=units),
                y=descent_data.depth,
                mode='lines+markers',
                name='Descent'
            )

            # Get and set the bottom data
            bottom_data = self.data[(self.data.time >= self.bottom_start) & (
                self.data.time <= (self.bottom_start + self.td_bottom_duration))]
            bottom = go.Scatter(
                x=num2date(bottom_data.time.tolist(), units=units),
                y=bottom_data.depth,
                mode='lines+markers',
                name='Bottom'
            )

            # Get and set the ascent data
            ascent_data = self.data[(self.data.time >= (self.bottom_start + self.td_bottom_duration)) & (
                self.data.time <= (self.data.time.max() - self.td_surface_duration))]
            ascent = go.Scatter(
                x=num2date(ascent_data.time.tolist(), units=units),
                y=ascent_data.depth,
                mode='lines+markers',
                name='Ascent'
            )

            # Get and set the surface data
            surface_data = self.data[self.data.time >= (
                self.data.time.max() - self.td_surface_duration)]

            surface = go.Scatter(
                x=num2date(surface_data.time.tolist(), units=units),
                y=surface_data.depth,
                mode='lines+markers',
                name='Surface'
            )

            layout = go.Layout(title='Dive starting at {}'.format(num2date(self.dive_start, units=units)),
                               xaxis=dict(title='Time'), yaxis=dict(title='Depth in Meters',autorange='reversed'))
            plot_data = [descent, bottom, ascent, surface]
            fig = go.Figure(data=plot_data, layout=layout)
            return py.iplot(fig)
        else:
            print("Insufficient data to plot.")

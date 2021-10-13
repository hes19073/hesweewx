# since.py
#
# A Search List Extension to provide aggregates since a given hour.
#
# python imports
import datetime
import syslog
import time

# weeWX imports
import weeutil.weeutil
import weewx.cheetahgenerator
import weewx.units

def logmsg(level, msg):
    syslog.syslog(level, 'since: %s' % msg)

def logdbg(msg):
    logmsg(syslog.LOG_DEBUG, msg)

def logdbg2(msg):
   if weewx.debug >= 2:
        logmsg(syslog.LOG_DEBUG, msg)

def loginf(msg):
    logmsg(syslog.LOG_INFO, msg)

def logerr(msg):
    logmsg(syslog.LOG_ERR, msg)


class Since(weewx.cheetahgenerator.SearchList):
    """SLE to provide aggregates since a given time of day."""

    def __init__(self, generator):
        # call our parent's initialisation
        super(Since, self).__init__(generator)

    def get_extension_list(self, timespan, db_lookup):
        """Returns a NewBinder object that supports aggregates since a given
           time.

            The NewBinder object implements the tag $since that allows
            inclusion of aggregates since the last occurrence of a give time of
            day, eg total rainfall since 9am, average temperature since midday.
            The signature of the $since tag is:

            $since([$hour=x]).obstype.aggregation[.optional_unit_conversion][.optional_formatting]

            where

            x is an integer from 0 to 23 inclusive representing the hour of the
            day

            obstype is a field in the archive table in use eg outTemp, inHumidiy
            or rain

            aggregation is an aggregate function supported by weewx (refer
            Customization Guide appendices)

            optional_unit_conversion and optional_formatting are optional weeWX
            unit conversion and formatting codes respectively

        Parameters:
            timespan: An instance of weeutil.weeutil.TimeSpan. This will hold
                      the start and stop times of the domain of valid times.

            db_lookup: This is a function that, given a data binding as its
                       only parameter, will return a database manager object.

        Returns:
            A NewBinder object with a timespan from "hour" o'clock to the
            report time
          """

        t1 = time.time()

        class NewBinder(weewx.tags.TimeBinder):

            def __init__(self, db_lookup, report_time,
                         formatter=weewx.units.Formatter(),
                         converter=weewx.units.Converter(), **option_dict):
                # call our parents initialisation
                super(NewBinder, self).__init__(db_lookup, report_time,
                                                formatter=formatter,
                                                converter=converter,
                                                **option_dict)

            def since(self, data_binding=None, hour=0):
                """Return a TimeSpanBinder for the period since 'hour'."""

                return since(self, data_binding, hour, True)

            def since(self, data_binding=None, hour=0, today=True):
                """Return a TimeSpanBinder for the period since 'hour'."""

                # get datetime obj for the time of our report
                stop_dt = datetime.datetime.fromtimestamp(timespan.stop)
                # the timespan we want may be wholly within today or may have
                # started yesterday, it depends on the value of the hour
                # parameter
                # first, get time obj for "hour" o'clock
                hour_t = datetime.time(hour)
                if stop_dt.hour >= hour:
                    # our timespan is solely within today, the start ts is at
                    # "hour" o'clock
                    # get datetime obj for "hour" o'clock today
                    hour_dt = datetime.datetime.combine(stop_dt, hour_t)
                else:
                    # our timespan starts yesterday and finishes today, so our
                    # start ts is "hour" o'clock yesterday
                    # first, get a datetime object for yesterday
                    yest_dt = stop_dt + datetime.timedelta(days=-1)
                    # get datetime obj for "hour" o'clock yesterday
                    hour_dt = datetime.datetime.combine(yest_dt, hour_t)
                # now get a ts, that is our start ts
                start_ts = time.mktime(hour_dt.timetuple())
                # and put together our timespan as a TimeSpan object
                tspan = weeutil.weeutil.TimeSpan(start_ts, timespan.stop)

                if today:
                    logdbg2("Since Start {}, Since stop {}".format(start_ts, timespan.stop))
                else:
                    # now subtract 1 day from our new datetime object
                    yest_dt = hour_dt + datetime.timedelta(days=-1)
                    # convert our yesterday datetime object to a timestamp
                    yest_ts = time.mktime(yest_dt.timetuple())

                    # and put together our timespan as a TimeSpan object
                    tspan = weeutil.weeutil.TimeSpan(yest_ts, start_ts)

                    logdbg2("SinceYesterday Start {}, Since stop {}".format(yest_ts, start_ts))

                # now return a TimespanBinder object, using the timespan we
                # just calculated
                return weewx.tags.TimespanBinder(tspan,
                                                 self.db_lookup,
                                                 context='hour',
                                                 data_binding=data_binding,
                                                 formatter=self.formatter,
                                                 converter=self.converter)

        tspan_binder = NewBinder(db_lookup,
                                timespan.stop,
                                self.generator.formatter,
                                self.generator.converter)

        t2 = time.time()
        logdbg2("Since SLE executed in %0.3f seconds" % (t2-t1))

        return [tspan_binder]

## forecast strip chart - Copyright 2012-2016 Matthew Wall
## $Id: forecast_strip.inc 1467 2016-03-14 15:36:18Z mwall $
## version = 0.1
##
## Include this file to display forecast data.
##
## To override the default settings in this file, use the following syntax in
## skin.conf or weewx.conf:
##
## [forecast_settings]
##     source = NWS
##     num_periods = 40
##
## To display a single forecast strip from a single source:
##
## #include forecast_strip.inc
##
## <body onload="populate_strip('forecast_strip', 'NWS');">
## <div id='forecast_strip'></div>
## </body>
##
## To display strips from multiple sources:
##
## #set global $forecast_settings['source'] = ['NWS', 'OWM']
## #set global $forecast_settings['num_periods'] = 300
## #include forecast_strip.inc
##
## <body onload="populate_strip('nws_strip', 'NWS'); populate_strip('owm_strip', 'OWM'">
## <div id='nws_strip'></div>
## <div id='owm_strip'></div>
## </body>

#if $varExists('forecast')

#import time
#set $t0 = time.time()

## Which forecasts should be displayed?
#set $strip_source = 'Aeris'

## How many forecast periods should be considered?
## Up to 40 for NWS, up to 240 for WU.  More periods take longer to generate.
#set $num_periods = 24

## Override defaults with anything specified in the skin
#if $varExists('forecast_settings')
#if $forecast_settings.has_key('source')
#set $strip_source = $forecast_settings.source
#end if
#if $forecast_settings.has_key('num_periods')
#set $num_periods = int($forecast_settings.num_periods)
#end if
#end if

#set $periods = $forecast.weather_periods($strip_source, max_events=$num_periods)

## These are the styles used by the forecast display as well as the generic
## javascript for populating the DOM elements with forecast data.  Ensure that
## these are included only once.
#if not $varExists('forecast_strip_included')
#set global $forecast_strip_included = 1
<style>
th {
  font-weight: normal;
  font-size: 80%;
}
td {
  font-weight: normal;
  text-align: right;
}
.qpf td {
  font-size: 80%;
}
.qsf td {
  font-size: 80%;
}
.date td {
  text-align: left;
}
.hour td {
  font-size: 80%;
}
.clouds img {
  width: 25px;
}
.sun img {
  width: 20px;
}
.moon img {
  width: 14px;
}
.windDir img {
  width: 15px;
}
.legend-img {
  width: 15px;
}
.day {
  font-size: 100%;
  font-weight: bold;
}
.tide_date {
  font-size: 80%;
}
.sources {
  font-size: 8pt;
  font-style: italic;
  color: #aaaaaa;
  padding-top: 10px;
}
</style>
<script>
var forecast_data = {};

function populate_strip(div_id, data_id) {
  if(! forecast_data[data_id]) return;
  var e = document.getElementById(div_id);
  if(! e) return;
  e.innerHTML = '';
  var tbl = document.createElement('table');
  tbl.appendChild(create_tr(forecast_data[data_id].date));
  tbl.appendChild(create_tr(forecast_data[data_id].hour));
  tbl.appendChild(create_tr(forecast_data[data_id].tempMax));
  tbl.appendChild(create_tr(forecast_data[data_id].temp));
  tbl.appendChild(create_tr(forecast_data[data_id].tempMin));
  tbl.appendChild(create_tr(forecast_data[data_id].dewpoint));
  tbl.appendChild(create_tr(forecast_data[data_id].humidity));
  tbl.appendChild(create_tr(forecast_data[data_id].windSpeed));
  tbl.appendChild(create_tr(forecast_data[data_id].windGust));
  tbl.appendChild(create_tr(forecast_data[data_id].windDir));
  tbl.appendChild(create_tr(forecast_data[data_id].clouds));
  tbl.appendChild(create_tr(forecast_data[data_id].pop));
  tbl.appendChild(create_tr(forecast_data[data_id].qpf));
  tbl.appendChild(create_tr(forecast_data[data_id].qsf));
  tbl.appendChild(create_tr(forecast_data[data_id].sun));
  tbl.appendChild(create_tr(forecast_data[data_id].moon));
  tbl.appendChild(create_tr(forecast_data[data_id].moonphase));
  var d = document.createElement('div');
  d.appendChild(tbl);
  e.appendChild(d);
  e.appendChild(create_summary(forecast_data[data_id].summary));
}

function create_tr(data) {
  var tr = document.createElement('tr');
  tr.className = data.className;
  var th = document.createElement('th');
  if(data.legend && data.legend != '') {
    var img = document.createElement('img');
    img.setAttribute('src', data.legend);
    img.className = 'legend-img';
    th.appendChild(img);
  }
  tr.appendChild(th);
  th = document.createElement('th');
  if(data.units != '') {
    th.innerHTML = data.units;
  }
  tr.appendChild(th);
  for(var i=0; i<data.values.length; i++) {
    var td = document.createElement('td');
    var v = data.values[i];
    if(data.td_type == 'icon') {
      if(v != '') {
        var img = document.createElement('img');
        img.setAttribute('src', 'xicons/' + v + '.png')
        td.appendChild(img);
      }
    } else if(data.td_type == 'txt') {
      if((v == '0.00' || v == '0') && data.skip_zeros) {
        ;
      } else {
        var n = document.createTextNode(v);
        td.appendChild(n);
        var bg = get_tint(v, data.className);
        if(bg != '') {
          td.style.background = bg;
//          td.style.border = '1px solid #dddddd';
        }
      }
    } else if(data.td_type == 'html') {
      if(v.colspan) { td.colSpan = v.colspan; }
      if(v.label) {
        td.innerHTML = v.label;
      } else {
        td.innerHTML = v;
      }
    }
    tr.appendChild(td);
  }
  return tr;
}

function create_summary(summary_data) {
  var d = document.createElement('div');
  d.className = 'sources';
  var html = summary_data.source + " forecast";
  if(summary_data.location != '') {
    html += " for " + summary_data.location;
  }
  if(summary_data.issued_ts != '') {
    html += " issued on " + summary_data.issued_ts;
  }
  html += "<br/>report generated in " + summary_data.elapsed + " s";
  d.innerHTML = html;
  return d;
}

function get_rgba(r, g, b, a) {
  return 'rgba('+r+','+g+','+b+','+a+')';
}

function get_tint(v, class_name, units) {
  if(v == '') return '';
//  var t_max; // maximum tint - anything over this is maximum high color
//  var t_min; // minimum tint - anything under this is maximum low color
//  var t_up; // upper threshold - start tinting when over this value
//  var t_dn; // lower threshold - start tinting when below this value
  if(class_name == 'pop') {
    var t_max = 100.0;
    var t_up = 30.0;
    var a = (v - t_up) / (t_max - t_up);
    return get_rgba(0, 144, 200, a);
  }
  if(class_name == 'qpf') {
    var t_max = 1.0; // inch
    var a = v / t_max;
    return get_rgba(0, 120, 250, a);
  }
  if(class_name == 'qsf') {
    var t_max = 6.0; // inch
    var a = v / t_max;
    return get_rgba(120, 120, 250, a);
  }
  if(class_name == 'windSpeed' || class_name == 'windGust') {
    var t_max = 40.0; // mph
    var a = (v > t_max) ? 1.0 : v / t_max;
    return get_rgba(255, 144, 0, a);
  }
  if(class_name.indexOf('temp') >= 0 || class_name == 'dewpoint') {
/*
    // red only, progressively darker with increase in temperature
    // kelvin makes the math easier
    var k = (v + 459.67) * 5.0 / 9.0;
    var t_max = 316;
    var t_min = 233;
    if(k > t_min) {
      var a = (k > t_max) ? 1.0 : k / t_max;
      return get_rgba(250, 0, 0, a);
    }
*/
    // blue for cold, red for warm, darker toward either end of spectrum
    // convert to celsius to make the math easier
    var c = (v - 32.0) * 5.0 / 9.0;
    var t_up = 10.0; // C
    var t_max = 40.0; // C
    var t_dn = 5.0; // C
    var t_min = -25.0; // C
    if(c > t_up) {
      var a = (c > t_max) ? 1.0 : (c - t_up) / (t_max - t_up);
      if(a > 0.8) { a = 0.8; }
      return get_rgba(200, 20, 20, a);
    } else if(c < t_dn) {
      var a = (c < t_min) ? 1.0 : (c - t_dn) / (t_min - t_dn);
      if(a > 0.8) { a = 0.8; }
      return get_rgba(60, 60, 250, a);
    }
  }
  if(class_name == 'humidity') {
    var t_max = 100.0;
    var t_up = 10.0;
    var a = (v - t_up) / (t_max - t_up);
    a = (a - 0.5 < 0) ? 0 : a - 0.5;
    return get_rgba(20, 120, 200, a);
  }
  if(class_name == 'moonphase') {
    var t_max = 100.0;
    var a = v / t_max;
    return get_rgba(200, 200, 100, a);
  }
  return '';
}
</script>
#end if ## forecast_strip_included

## Strip chart shows arrows pointing with wind flow, not into the wind
#set $tWind = {'N':'tS', 'NNE':'tSSW', 'NE':'tSW', 'ENE':'tWSW', 'E':'tW', 'ESE':'tWNW', 'SE':'tNW', 'SSE':'tNNW', 'S':'tN', 'SSW':'tNNE', 'SW':'tNE', 'WSW':'tENE', 'W':'tE', 'WNW':'tESE', 'NW':'tSE', 'NNW':'tSSE'}

#set $strip_location = ''
#set $strip_issued_ts = ''

#if len($periods) > 0
#set $strip_location = $periods[0].location
#set $strip_issued_ts = $periods[0].issued_ts
#end if

<script>
forecast_data.$strip_source = {
  'id': "$strip_source",
  'date': {
    'className': 'date',
    'units': '',
    'td_type': 'html',
    'values':[ #slurp
#set $days = dict()
#for $period in $periods
  #set $thisdate = $period.event_ts.format('%Y.%m.%d')
  #set $thisdow = $period.event_ts.format('%a')
  #if $days.get($thisdate)
    #set $days[$thisdate]['cols'] = $days[$thisdate]['cols'] + 1
  #else
    #set $days[$thisdate] = dict()
    #set $days[$thisdate]['cols'] = 1
    #set $days[$thisdate]['dow'] = $thisdow
  #end if
#end for
#for $day in sorted($days)
  #set $label = ''
  #if $days[$day]['cols'] > 3
    #set $label = '<span class="day">%s</span><br/><span class="date">%s</span>' % ($days[$day]['dow'], $day)
  #end if
{'colspan': $days[$day]['cols'], 'label': '$label'}, #slurp
#end for
  ]},
  'hour': {
    'className': 'hour',
    'units': '',
    'td_type': 'txt',
    'values':[ #slurp
#for $period in $periods
"$period.event_ts.format('%Hh')", #slurp
#end for
  ]},
  'tempMax': {
    'className': 'temp',
    'units': '$unit.label.outTemp',
    'td_type': 'txt',
    'values':[ #slurp
#for $period in $periods
"$period.tempMax.nolabel('%.0f', '')", #slurp
#end for
  ]},
  'tempMin': {
    'className': 'temp',
    'units': '$unit.label.outTemp',
    'td_type': 'txt',
    'values':[ #slurp
#for $period in $periods
"$period.tempMin.nolabel('%.0f', '')", #slurp
#end for
  ]},
  'temp': {
    'className': 'temp',
    'legend': 'xicons/thermometer-red.png',
    'units': '$unit.label.outTemp',
    'td_type': 'txt',
    'values':[ #slurp
#for $period in $periods
"$period.temp.nolabel('%.0f', '')", #slurp
#end for
  ]},
  'dewpoint': {
    'className': 'dewpoint',
    'legend': 'xicons/thermometer-dewpoint.png',
    'units': '$unit.label.dewpoint',
    'td_type': 'txt',
    'values':[ #slurp
#for $period in $periods
"$period.dewpoint.nolabel('%.0f', '')", #slurp
#end for
  ]},
  'humidity': {
    'className': 'humidity',
    'legend': 'xicons/thermometer-blue.png',
    'units': '%',
    'td_type': 'txt',
    'skip_zeros': true,
    'values':[ #slurp
#for $period in $periods
"$period.humidity.nolabel('%.0f', '')", #slurp
#end for
  ]},
  'windSpeed': {
    'className': 'windSpeed',
    'legend': 'xicons/flag.png',
    'units': '$unit.label.wind',
    'td_type': 'txt',
    'values':[ #slurp
#for $period in $periods
"$period.windSpeed.nolabel('%.0f', '')", #slurp
#end for
  ]},
  'windGust': {
    'className': 'windGust',
    'units': '$unit.label.wind',
    'td_type': 'txt',
    'values':[ #slurp
#for $period in $periods
"$period.windGust.nolabel('%.0f', '')", #slurp
#end for
  ]},
  'windDir': {
    'className': 'windDir',
    'units': '',
    'td_type': 'icon',
    'values':[ #slurp
#for $period in $periods
#set $wd = $tWind.get($period.windDir)
"$wd", #slurp
#end for
  ]},
  'clouds': {
    'className': 'clouds',
    'units': '',
    'td_type': 'icon',
    'values':[ #slurp
#for $period in $periods
  #set $clouds_img = ''
  #if $period.clouds is not None
    #set $alm = $forecast.almanac(ts=$period.event_ts.raw+10)
    #set $sunrise_ts = $alm.sunrise.raw
    #set $sunset_ts = $alm.sunset.raw
    #if $sunrise_ts < $period.event_ts.raw < $sunset_ts
      #set $clouds_img = $period.clouds
    #else
      #set $clouds_img = $period.clouds + 'n'
    #end if
  #end if
"$clouds_img", #slurp
#end for
  ]},
  'pop': {
    'className': 'pop',
    'legend': 'xicons/pop.png',
    'units': '%',
    'td_type': 'txt',
    'skip_zeros': true,
    'values':[ #slurp
#for $period in $periods
"$period.pop.nolabel('%.0f', '')", #slurp
#end for
  ]},
  'qpf': {
    'className': 'qpf',
    'legend': 'xicons/raindrop.png',
    'units': '$unit.label.rain',
    'td_type': 'txt',
    'skip_zeros': true,
    'values':[ #slurp
#for $period in $periods
"$period.qpf.nolabel('%.2f', '')", #slurp
#end for
  ]},
  'qsf': {
    'className': 'qsf',
    'legend': 'xicons/snowflake.png',
    'units': '$unit.label.rain',
    'td_type': 'txt',
    'skip_zeros': true,
    'values':[ #slurp
#for $period in $periods
"$period.qsf.nolabel('%.2f', '')", #slurp
#end for
  ]},
  'sun': {
    'className': 'sun',
    'legend': 'xicons/sunriseset.png',
    'units': '',
    'td_type': 'icon',
    'values':[ #slurp
#for $period in $periods
  #set $img = ''
  #set $alm = $forecast.almanac(ts=$period.event_ts.raw+10)
  #set $sunrise_ts = $alm.sunrise.raw
  #set $sunset_ts = $alm.sunset.raw
  #if $period.event_ts.raw < $sunrise_ts <= $period.event_ts.raw + $period.duration
    #set $img = 'sunrise'
  #end if
  #if $period.event_ts.raw < $sunset_ts <= $period.event_ts.raw + $period.duration
    #set $img = 'sunset'
  #end if
"$img", #slurp
#end for
  ]},
  'moon': {
    'className': 'moon',
    'legend': 'xicons/moonriseset.png',
    'units': '',
    'td_type': 'icon',
    'values':[ #slurp
#for $period in $periods
  #set $img = ''
  #set $alm = $forecast.almanac(ts=$period.event_ts.raw+10)
  #set $moonrise_ts = $alm.moon.rise.raw
  #set $moonset_ts = $alm.moon.set.raw
  #if $period.event_ts.raw < $moonrise_ts <= $period.event_ts.raw + $period.duration
    #set $img = 'moonrise'
  #end if
  #if $period.event_ts.raw < $moonset_ts <= $period.event_ts.raw + $period.duration
    #set $img = 'moonset'
  #end if
"$img", #slurp
#end for
  ]},
  'moonphase': {
    'className': 'moonphase',
    'legend': 'xicons/moonphase.png',
    'units': '',
    'td_type': 'txt',
    'values':[ #slurp
#for $period in $periods
  #set $alm = $forecast.almanac(ts=$period.event_ts.raw+10)
"$alm.moon_fullness", #slurp
#end for
  ]},
  'summary': {
    'source': "$strip_source",
    'location': "$strip_location",
    'issued_ts': "$strip_issued_ts",
#set $elapsed = "%.3f" % (time.time() - $t0)
    'elapsed': "$elapsed"
  }
};
</script>

#else

<!-- forecast_strip: forecast search list extension is not installed -->

#end if

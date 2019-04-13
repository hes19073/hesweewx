#errorCatcher Echo
#encoding UTF-8

## Which forecast should be displayed?  options are WU or NWS
#set $forecast_source = 'WU'
## How many forecast periods should be considered?
#set $num_periods = 40
#set $wloc = ''
#set $wts = ''
#set $lastday = None
#set $periods = $forecast.weather_periods($forecast_source, max_events=$num_periods)
#for $period in $periods
  #set $thisday = $period.event_ts.format('%d')
  #set $thisdate = $period.event_ts.format('%Y.%m.%d')
  #set $smryid = $forecast_source + '.' + $thisdate
  #set $hourid = $forecast_source + '.' + $thisdate + '.hours'
  #set $alm = $forecast.almanac(ts=$period.event_ts.raw)
  #set $nextday_ts = time.mktime(time.strptime($thisdate + ' 00:00', '%Y.%m.%d %H:%M')) + 24*3600
  #set $sunrise_ts = $alm.sunrise.raw
  #set $sunset_ts = $alm.sunset.raw
  #set $moonrise_ts = $alm.moon.rise.raw
  #set $moonset_ts = $alm.moon.set.raw
  #set $wts = $period.issued_ts

  #if $lastday != $thisday

   #set $lastday = $thisday
   #set $summary = $forecast.weather_summary($forecast_source, $period.event_ts.raw, periods=$periods)
   #set $wloc = $summary.location
   <p>
   #if $summary.clouds is not None
       #set $simg = 'xicons/' + $summary.clouds + '.png'
        <img class='outlook-img' src='$simg' alt='$summary.clouds' title='$forecast.label('Weather', $summary.clouds)' />
   #end if
    $summary.event_ts.format('%A'),&nbsp;der&nbsp;$summary.event_ts.format('%d %b %Y'):
    Der Himmel&nbsp;$forecast.label('Weather', $summary.clouds).&nbsp;
    Die Tagestemperatur zwischen&nbsp;$summary.tempMin&nbsp;und&nbsp;$summary.tempMax.&nbsp;
    Die gefühlt Temperatur zwischen&nbsp;$summary.feelslikeMin&nbsp;und&nbsp;$summary.feelslikeMax.
    Wind aus&nbsp;$summary.windDir,&nbsp;
    mit einer Geschwindigkeit von&nbsp;$summary.windSpeed,&nbsp;in Spitzen&nbsp;$summary.windSpeedMax.
    Die Luftfeuchtigkeit bei ca.&nbsp;$summary.humidity.&nbsp;
    Die Niederschlagswahrscheinlichkeit am Tag bei&nbsp;$summary.pop.</p><hr />
  #end if   ## lastday != thisday
#end for    ## period in periods

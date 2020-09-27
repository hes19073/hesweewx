#encoding UTF-8
##  links_forecast.inc 2749 2018-11-26 18:15:24Z hes $
#import time
#set $windT_dir_dict = {"N" : "Nord", "NNE" : "Nordnordost", "NE" : "Nordost", "ENE" : "Ostnordost", "E" : "Ost", "ESE" : "Ostsüdost", "SE" : "Südost", "SSE" : "Südsüdost", "S" : "Süd", "SSW" : "Südsüdwest", "SW" : "Südwest", "WSW" : "Westsüdwest", "W" : "West", "WNW" : "Westnordwest", "NW" : "Nordwest", "NNW" : "Nordnordwest"}

## DS = Aeris
#set $summaryDS = $forecast.weather_summary('Aeris')
#set $ddDS = $forecast.label('Weather', $summaryDS.windDir)
#set $windDS_text = $windT_dir_dict.get($ddDS)

#set $timeFormat = "%H:%M"
#try
    #set $timenextupdate=time.strftime($timeFormat,time.localtime($time.time() + float($current.interval.raw)*60))
#except
    #set $timenextupdate = 0
#end try

<div class='hes'>
 <div class='hesbox'>
<!-- Vantage Pro2 Station -->
#if $current.forecastRule.raw is not None
    #set $VPn = $current.forecastRule.raw
#else
    #set $VPn = '46'
#end if

#set $VPn = int($VPn)
#set $VPn = str($VPn)
#if $current.outTemp.raw < 0
    #set $VPnumber = 'xicons/VPnumbers/' + $VPn + 's.gif'
#else
    #set $VPnumber = 'xicons/VPnumbers/' + $VPn + '.gif'
#end if

   <p><img alt="Wetter" src="$VPnumber" /><br>
    <b>VantagePro 2:</b> $vantageText<br>
   Prognose erstellt:&nbsp;$current.dateTime &nbsp;Uhr</p>
  <hr />

<!-- Zambretti Prognose -->
  #if $forecast.label('Zambretti', $forecast.zambretti.code) is not None
  <p><b>Zambretti:</b>&nbsp;$forecast.label('Zambretti', $forecast.zambretti.code)<br />
   Prognose erstellt:&nbsp;$forecast.label('Zambretti', $forecast.zambretti.event_ts.format('%d.%m.%Y %H:%M'))&nbsp;Uhr</p>
  #else
  <p><b>Zambretti:</b></p>
  #end if
<hr />

<!-- AerisWeather Prognose -->
  <p>
    #if $summaryDS.clouds is not None
        #set $simgDS = 'xicons/' + $summaryDS.clouds + '.png'
        <img src='$simgDS' alt='$summaryDS.clouds' title='$forecast.label('Weather', $summaryDS.clouds)' />
    #end if
    <br>
    <b>AerisWeather:</b>
    $forecast.label('Weather', $summaryDS.clouds)<br>
    Temperatur Max: $forecast.label('Weather', $summaryDS.tempMax) bis Min: $forecast.label('Weather', $summaryDS.tempMin)<br>
    Wind bei: $forecast.label('Weather', $summaryDS.windSpeed)&nbsp;
    in Spitzen: $forecast.label('Weather', $summaryDS.windGust)<br>
    Windrichtung: <b>$windDS_text</b><br>
    Regenrisiko: $forecast.label('Weather', $summaryDS.pop)<br>
    <br />
    Wetter:
    <a href='https://wx.aerisweather.com/local/de/klein%20rogahn' target='_blank'><b> Powerd by AerisWeather</b></a>
  </p>
   <hr />

<!-- Bild Wetter Dach -->
  <h3>Wetter Kamera Richtung SW</h3>
   <a href="xicons/wet/snapshot.jpg">
   <img src="xicons/wet/snapshot.jpg" width="300" height="180" alt="Wetter aktuell" /></a>
   <hr />
   <p><font color='red'>Sonne</font>&nbsp;<font color='blue'>Mond</font></p>
   <img src="daySonne.png" alt="Sonnenstand" style="width:300px; height:175px;" />
   <hr />
   <p>WeeWX Aktualisierung:&nbsp;$timenextupdate Uhr</p>
   <hr />
   DWD Warnungen: $warn_update Uhr<br>
   Aeris Warnung: $alerts_update Uhr<br>
   Aeris  Wetter: $forecast_updated Uhr
   
   <hr />
 </div>
</div>

#encoding UTF-8
##  links_forecast.inc 2749 2018-11-26 18:15:24Z hes $

#set $windT_dir_dict = {"N" : "Nord", "NNE" : "Nordnordost", "NE" : "Nordost", "ENE" : "Ostnordost", "E" : "Ost", "ESE" : "Ostsüdost", "SE" : "Südost", "SSE" : "Südsüdost", "S" : "Süd", "SSW" : "Südsüdwest", "SW" : "Südwest", "WSW" : "Westsüdwest", "W" : "West", "WNW" : "Westnordwest", "NW" : "Nordwest", "NNW" : "Nordnordwest"}

#set $summaryDS = $forecast.weather_summary('DS')
#set $ddDS = $forecast.label('Weather', $summaryDS.windDir)
#set $windDS_text = $windT_dir_dict.get($ddDS)

<div class='hes'>
 <div class='hesbox'>
  #if $forecast.label('Zambretti', $forecast.zambretti.code) is not None
  <p><b>Zambretti:</b>&nbsp;$forecast.label('Zambretti', $forecast.zambretti.code)<br />
   Prognose erstellt:&nbsp;$forecast.label('Zambretti', $forecast.zambretti.event_ts.format('%d.%m.%Y %H:%M'))&nbsp;Uhr</p>
  #else
  <p><b>Zambretti:</b></p>
  #end if
<hr />

  <p>
    #if $summaryDS.clouds is not None
        #set $simgDS = 'xicons/' + $summaryDS.clouds + '.png'
        <img src='$simgDS' alt='$summaryDS.clouds' title='$forecast.label('Weather', $summaryDS.clouds)' />
    #end if
    <br>
    <b>DarkSky:</b>
    $forecast.label('Weather', $summaryDS.clouds)<br>
    Temperatur Max: $forecast.label('Weather', $summaryDS.tempMax) bis Min: $forecast.label('Weather', $summaryDS.tempMin)<br>
    Wind bei: $forecast.label('Weather', $summaryDS.windSpeed)&nbsp;
    in Spitzen: $forecast.label('Weather', $summaryDS.windGust)<br>
    Windrichtung: <b>$windDS_text</b><br>
    Regenrisiko: $forecast.label('Weather', $summaryDS.pop)<br>
#if $latest($data_binding='wdsupp_binding').visibility_km.has_data
    Sichtweite ca.: $latest($data_binding='wdsupp_binding').visibility_km
#end if
    <br />
    Wetter:
    <a href='https://darksky.net/poweredby/' target='_blank'><b> Powerd by Dark Sky</b></a>
    <br>Heute:&nbsp;$day_summary
    <br>Woche:&nbsp;$week_summary
    <br>Prognose erstellt:&nbsp;$forecast_updated&nbsp;Uhr
  </p>
  <hr />

#if $latest($data_binding='wdsupp_binding').vantageForecastNumber.has_data
        #set $VPn = $latest($data_binding='wdsupp_binding').vantageForecastNumber.raw
#else
        #set $VPn = 46
#end if
    #set $VPn = int($VPn)
    #set $VPn = str($VPn)
    #if $current.outTemp.raw < 0
        #set $VPnumber = 'xicons/VPnumbers/' + $VPn + 's.gif'
    #else
        #set $VPnumber = 'xicons/VPnumbers/' + $VPn + '.gif'
    #end if

   <p><img alt="Wetter" src="$VPnumber" /><br>
   <b>VantagePro 2:</b> $latest($data_binding='wdsupp_binding').vantageForecastRule.raw<br>
       Prognose erstellt:&nbsp;$latest($data_binding='wdsupp_binding').dateTime&nbsp;Uhr</p>

  <hr />
  <h3>Wetter Kamera Richtung SW</h3>
   <a href="xicons/wet/snapshot.jpg">
   <img src="xicons/wet/snapshot.jpg" width="300" height="180" alt="Wetter aktuell" /></a>
   <hr />
   <p><font color='red'>Sonne</font>&nbsp;<font color='blue'>Mond</font></p>
   <img src="daySonne.png" alt="Sonnenstand" style="width:300px; height:175px;" />
   <hr />
   <p>Python: $station.python_version</p>
 </div>
</div>

#encoding UTF-8
##  links.inc 2749 2018-11-26 18:15:24Z hes $

#set $windT_dir_dict = {"N" : "Nord", "NNE" : "Nordnordost", "NE" : "Nordost", "ENE" : "Ostnordost", "E" : "Ost", "ESE" : "Ostsüdost", "SE" : "Südost", "SSE" : "Südsüdost", "S" : "Süd", "SSW" : "Südsüdwest", "SW" : "Südwest", "WSW" : "Westsüdwest", "W" : "West", "WNW" : "Westnordwest", "NW" : "Nordwest", "NNW" : "Nordnordwest"}

#set $summary = $forecast.weather_summary('WU')
#set $dd = $forecast.label('Weather', $summary.windDir)
#set $wind_text = $windT_dir_dict.get($dd)

<div class='hes'>
 <div class='hesbox'>
  <p><b>Zambretti:</b>&nbsp;$forecast.label('Zambretti', $forecast.zambretti.code)<br />
   Prognose erstellt am:&nbsp;$forecast.label('Zambretti', $forecast.zambretti.event_ts.format('%d.%m.%Y %H:%M'))</p>
  <hr />
 #if $current.outTemp.raw is not None
    #set $VPn = 44 ##$latest($data_binding='wdsupp_binding').vantageForecastNumber.raw
    #set $VPn = int($VPn)
    #set $VPn = str($VPn)
    #if $current.outTemp.raw < 0
        #set $VPnumber = 'xicons/VPnumbers/' + $VPn + 's.gif'
    #else
        #set $VPnumber = 'xicons/VPnumbers/' + $VPn + '.gif'
    #end if
 #end if
   <p><img alt="Wetter" src="$VPnumber" /><br>
   <b>VantagePro 2:</b> $latest($data_binding='wdsupp_binding').vantageForecastRule.raw</p>
  <hr />
#if $Extras.has_key('forecast_enabled') and $Extras.forecast_enabled == '0'
  <p>
    $current_obs_icon <br />
    <b>DarkSky:</b>
    $current_obs_summary <br />
    Prognose erstellt am: $forecast_updated <br>
    #set $current_tem = ("%.1f" % $current_temp).replace(".",",")
    #set $current_apptem = ("%.1f" % $current_apptemp).replace(".",",")
    #set $current_win = ("%.1f" % $current_wind).replace(".",",")
    #set $visibilit = ("%.3f" % $visibility).replace(".",",")
    Temperatur: $current_tem $unit.label.outTemp : gefühlt: $current_apptem $unit.label.outTemp<br>
    Windgeschwindigkeit: $current_win $unit.label.windSpeed<br>
   Sichtweite: $visibilit &nbsp;$visibility_unit
  </p>
  <hr />
#end if
  <p>Wind heute meist aus&nbsp;<b>$wind_text</b></p>
  <hr />
  <h3>Wetter Kamera Richtung SW</h3>
   <a href="xicons/wet/snapshot.jpg">
   <img src="xicons/wet/snapshot.jpg" width="300" height="180" alt="Wetter aktuell" /></a>
   <hr />
   #if $latest($data_binding='wdsupp_binding').visibility_km.raw > 0.0
     <p>WU-Sichtweite ca.: $latest($data_binding='wdsupp_binding').visibility_km</p>
   #else
     <p>&nbsp;</p>
   #end if
   <hr />
   <img src="daySonne.png" alt="Sonnenstand" style="width:300px; height:175px;" />
 </div>
</div>

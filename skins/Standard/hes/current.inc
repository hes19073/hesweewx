#encoding UTF-8
## hes: current.inc  2015-02-23 18:24:18Z hes $

<div class="stats">
 <div class="stats_header">
      Aktuelle Werte
 </div>
 <table>
  <tbody>
   <tr>
    <td class="stats_label">Temperatur<br />&nbsp;</td>
    <td class="stats_data" style="$decorator_color('tempO', $current.outTemp.raw)">$current.outTemp
     &nbsp;&nbsp; $decorator_text('tempO', $current.outTemp.raw)&nbsp;&nbsp;&nbsp;($current.outTemp.degree_F)</td>
   </tr>
   <tr>
    <td class="stats_label">maximale Temperatur<br />&nbsp;</td>
    <td class="stats_data">$day.outTemp.historical_max
        im Jahre $day.outTemp.historical_maxtime.format("%Y") </td>
   </tr>
   <tr>
    <td class="stats_label">minimale Temperatur<br />&nbsp;</td>
    <td class="stats_data">$day.outTemp.historical_min
        im Jahre $day.outTemp.historical_mintime.format("%Y") </td>
   </tr>
   <tr>
    #set $deltaT = $current.outTemp.raw - $current.wetBulb.raw
    #set $DeltaT = "%.1f" % $deltaT + " &deg;C"
    <td class="stats_label">DeltaT<br />Luft Temperaturdifferenz</td>
    <td class="stats_data" style="$decorator_color('tempO', $deltaT)">$DeltaT</td>
   </tr>
   <tr>
    <td class="stats_label">scheinbare<br />Temperatur</td>
    <!-- <td class="stats_data"><b>$current.appTemp</b></td> -->
    <td class="stats_data" style="$decorator_color('heattemp', $current.appTemp.raw)">$current.appTemp 
     &nbsp;&nbsp;$decorator_text('heattemp', $current.appTemp.raw)&nbsp;&nbsp;&nbsp;($current.appTemp.degree_F)</td>
   </tr>
   <tr>
    <td class="stats_label">Windchill
     <div class="popup" onclick="myFunction1()"> <sup>( Info )</sup>
      <span class="popuptext" id="myPopup1">Der Windchill (engl.) bzw. die Windkühle (auch Windfrösteln) beschreibt den 
                                            Unterschied zwischen der gemessenen Lufttemperatur und der gefühlten Temperatur 
                                            in Abhängigkeit von der Windgeschwindigkeit.
                                            Er findet unterhalb von ca. 10 C° Anwendung.</span></div>
    <br />&nbsp;</td>
    <!-- <td class="stats_data">$current.windchill</td> -->
    <td class="stats_data" style="$decorator_color('chill_C', $current.windchill.raw)">$current.windchill
     &nbsp;$decorator_text('chill_C', $current.windchill.raw)</td>
   </tr>
   <tr>
    <td class="stats_label">Hitzeindex
     <div class="popup" onclick="myFunction2()"> <sup>( Info )</sup>
      <span class="popuptext" id="myPopup2">Der Hitzeindex bescheibt die gefühlte Temperatur auf Basis 
                                            der gemessenen Lufttemperatur sowie vor 
                                            allem der relativen Luftfeuchtigkeit.
                                            Er findet ab 27 C° Anwendung.</span></div>
    <br />&nbsp;</td>
    <!-- <td class="stats_data">$current.heatindex</td> -->
    <td class="stats_data" style="$decorator_color('heatindex', $current.heatindex.raw)">$current.heatindex 
     &nbsp;$decorator_text('heatindex', $current.heatindex.raw)</td>
   </tr>
   <tr>
    <td class="stats_label">Humidex<br />&nbsp;</td>
    <!-- <td class="stats_data">$current.humidex</td> -->
    <td class="stats_data" style="$decorator_color('humidex', $current.humidex.raw)">
     &nbsp;&nbsp; $decorator_text('humidex', $current.humidex.raw)</td>
   </tr>
   <tr>
   <td class="stats_label">Taupunkt<br />&nbsp;</td>
   <td class="stats_data">$current.dewpoint&nbsp;&nbsp;&nbsp;($current.dewpoint.degree_F)</td>
   </tr>
   <tr>
    <td class="stats_label">Luftfeuchte<br />&nbsp;</td>
    <td class="stats_data">$current.outHumidity</td>
   </tr>
#if $latest($data_binding='air_binding').inHumidity is not None
   <tr>
    <td class="stats_label">Luftfeuchte<br />AQI²</td>
    <td class="stats_data">$latest($data_binding='air_binding').inHumidity</td>
   </tr>
#end if
#if $latest($data_binding='airCar_binding').humiAir is not None
   <tr>
    <td class="stats_label">Luftfeuchte<br />Carport</td>
    <td class="stats_data">$latest($data_binding='airCar_binding').humiAir</td>
   </tr>
#end if
   <tr>
    <td class="stats_label">Luftfeuchte<br />absolut&nbsp;</td>
    <td class="stats_data">$current.absolutF</td>
   </tr>
   <tr>
    <td class="stats_label">Dampfdichte<br />tatsächlich&nbsp;</td>
    <td class="stats_data">$current.AVP</td>
   </tr>
   <tr>
    <td class="stats_label">Dampfdruck<br />(Wasserdampfdruck)</td>
    <td class="stats_data">$current.dampfDruck.formatted&nbsp;hPa</td>
   </tr>
   <tr>
    <td class="stats_label">Luftdruck<br />&nbsp;</td>
    <td class="stats_data">$current.barometer&nbsp;&nbsp;&nbsp;($current.barometer.inHg)</td>
   </tr>
   <tr>
    <td class="stats_label">Luftdruck Trend ($trend.time_delta.hour.format("%.0f"))<br />&nbsp;</td>
    <!-- <td class="stats_data">$trend.barometer</td> -->
    <td class="stats_data" style="$decorator_color('barotrend', $trend.barometer.raw)">$trend.barometer
     &nbsp;&nbsp; $decorator_text('barotrend', $trend.barometer.raw)
    </td>
   </tr>
 <!--  <tr>
    <td class="stats_label">Luftdruck<br />Änderungsrate</td>
    <td class="stats_data">$current.barometerRate</td>
   </tr> -->
#if $latest($data_binding='airCar_binding').presAir is not None
   <tr>
    <td class="stats_label">Luftdruck<br />Carport (BMP 180)</td>
    <td class="stats_data">$latest($data_binding='airCar_binding').presAir</td>
   </tr>
#end if
#if $latest($data_binding='airCar_binding').slp_A is not None
   <tr>
    <td class="stats_label">Luftdruck SLP<br />Carport (BMP 180)</td>
    <td class="stats_data">$latest($data_binding='airCar_binding').slp_A</td>
   </tr>
#end if
#if $latest($data_binding='airCar_binding').altiAir is not None
   <tr>
    <td class="stats_label">Altitude<br />Carport (BMP 180)</td>
    <td class="stats_data">$latest($data_binding='airCar_binding').altiAir</td>
   </tr>
#end if
   <tr>
    <td class="stats_label">Luftdichte<br />&nbsp;</td>
    <td class="stats_data">$current.airDensity</td>
   </tr>
   <tr>
    <td class="stats_label">Wind<br />&nbsp;</td> <!-- 14.03.2020 Davis Neu -->
    <td class="stats_data" style="$decorator_color('windBof', $current.windSpeed.raw)"><b>$current.windSpeed</b> 
    #if $current.windSpeed.raw == 0.0
        <b>&nbsp;Windstill</b>
    #else
        <b>aus&nbsp;$current.windDir ($current.windDir.ordinal_compass)</b>
    #end if
    </td>
   </tr>
   <tr>
    <td class="stats_label">Wind in Beaufort<br />&nbsp;</td>
    <td class="stats_data" style="$decorator_color('windBof', $current.windSpeed.raw)">
     &nbsp; $decorator_text('windBof', $current.windSpeed.raw)</td>
   </tr>
   <tr>
    <td class="stats_label">Wind<br />Böen</td>
    <td class="stats_data" style="$decorator_color('windBof', $current.windGust.raw)"><b>$current.windGust</b>
    #if $current.windGust.raw == 0.0
        <b>&nbsp;Windstill</b>
    #else
        <b>aus&nbsp;$current.windGustDir ($current.windGustDir.ordinal_compass)</b>
    #end if
    </td>
   </tr>
   <tr>
    <td class="stats_label">Böe in Beaufort<br />&nbsp;</td>
    <td class="stats_data" style="$decorator_color('windBof', $current.windGust.raw)">
     &nbsp; $decorator_text('windBof', $current.windGust.raw)</td>
   </tr>
   <tr>
    <td class="stats_label">Winddruck<br />&nbsp;</td>
    <td class="stats_data">$current.windDruck</td>
   </tr>
   <tr>
    <td class="stats_label">Windweg<br />seit Mitternacht</td>
    <td class="stats_data">$current.windrun<br />$day.windrun.sum</td>
   </tr>
   <tr>
    <td class="stats_label">Niederschlag,<br>der letzten 5 Minuten</td>
    <td class="stats_data">$current.rain</td>
   </tr>
  <tr>
    <td class="stats_label">Regenintensität,<br />der letzten 5 Minuten</td>
    <td class="stats_data">$current.rainRate</td>
  </tr>
   <tr>
    <td class="stats_label">Niederschlag heute<br />seit Mitternacht</td>
    <td class="stats_data">$day.rain.sum</td>
  </tr>
  <tr>
    <td class="stats_label">Regenintensität<br />&nbsp;</td>
    <td class="stats_data">$day.rainRate.max</td>
  </tr>
  <tr>
    <td class="stats_label">Letzter Niederschlag<br />&nbsp;</td>
    <td class="stats_data">$lastrain_day <br /> $lastrain_delta_time</td>
  </tr>
  <tr>
    <td class="stats_label">Schneefall<br />aktuell&nbsp;</td>
    <td class="stats_data">$current.snow</td>
  </tr>
  <tr>
    <td class="stats_label">Schneeintensität<br />&nbsp;</td>
    <td class="stats_data">$day.snowRate.max</td>
  </tr>
  <tr>
    <td class="stats_label">Letzter Schneefall<br />&nbsp;</td>
    <td class="stats_data">$lastsnow_day <br /> $lastsnow_delta_time</td>
  </tr>
  <tr>
    <td class="stats_label">Schneedecke<br />aktuell bei ca.</td>
    <td class="stats_data">$current.snowTotal</td>
  </tr>
  <tr>
    <td class="stats_label">Letzte Schneedecke<br />&nbsp;</td>
    <td class="stats_data">$lastsnowT_day <br /> $lastsnowT_delta_time</td>
  </tr>
   <tr>
    <td class="stats_label">ET am Tag<br />Evapotranspiration</td>
    <td class="stats_data">$day.ET.sum</td>
   </tr>
  <tr><td>Niederschlag<br />Verdunstung</td><td>Seit dem 04.05.2019</td></tr>
  <tr>
    <td class="stats_label">Wasserbilanz <br />seit Mitternacht</td>
    #set $wasser_day = $day.rain.sum.raw - $day.ET.sum.raw
    #set $WasserDay = ("{:.2f}".format($wasser_day));
    #if $wasser_day < 0.0
    <td class="stats_data" style="background-color: coral">$WasserDay&nbsp;mm</td>
    #else
    <td class="stats_data" style="background-color: limegreen">$WasserDay&nbsp;mm</td>
    #end if
  </tr>
  <tr>
    <td class="stats_label">Wasserbilanz <br />Dieses Jahr</td>
    #set $wasser_year = $year.rain.sum.raw - $year.ET.sum.raw
    #set $WasserYear = ("{:.2f}".format($wasser_year));
    #if $wasser_year < 0.0
    <td class="stats_data" style="background-color: coral">$WasserYear&nbsp;mm</td>
    #else
    <td class="stats_data" style="background-color: limegreen">$WasserYear&nbsp;mm</td>
    #end if
  </tr>
  <tr><td>1-Wire OWFS USB<br />Temperatur</td><td>Seit dem 10.08.2015&nbsp;</td></tr>
#if $latest($data_binding='airCar_binding').tem_A is not None
   <tr>
    <td class="stats_label">Temperatur<br />Carport (BMP 180)</td>
    <td class="stats_data" style="$decorator_color('tempO', $latest($data_binding='airCar_binding').tem_A.raw)">
             $latest($data_binding='airCar_binding').tem_A</td>
   </tr>
#end if
#if $day.extraTemp9.has_data
  <tr>
   <td class="stats_label">Carport<br />&nbsp;</td>
   <td class="stats_data" style="$decorator_color('tempO', $current.extraTemp9.raw)">$current.extraTemp9</td>
  </tr>
#end if
#if $day.extraTemp4.has_data
  <tr>
   <td class="stats_label">Garten<br />&nbsp;</td>
   <td class="stats_data" style="$decorator_color('tempO', $current.extraTemp4.raw)">$current.extraTemp4</td>
  </tr>
#end if
#if $day.extraTemp8.has_data
  <tr>
   <td class="stats_label">Schwimmsteg<br />ca. 1,80 m&nbsp;</td>
   <td class="stats_data" style="$decorator_color('tempO', $current.extraTemp8.raw)">$current.extraTemp8</td>
  </tr>
#end if
  <tr><td>1-Wire OWFS USB<br/>Wassertemperatur</td><td>Seit dem 10.08.2015</td></tr>
#if $day.extraTemp6.has_data
  <tr>
   <td class="stats_label">Gartenteich <br />Goldfisch</td>
   <td class="stats_data">$current.extraTemp6</td>
  </tr>
#end if
#if $day.extraTemp1.has_data
  <tr>
   <td class="stats_label">Teich<br />klein&nbsp;</td>
   <td class="stats_data">$current.extraTemp1</td>
  </tr>
#end if
#if $day.extraTemp2.has_data
  <tr>
   <td class="stats_label">Schwimmteich<br />&nbsp;</td>
   <td class="stats_data">$current.extraTemp2</td>
  </tr>
#end if
#if $day.extraTemp3.has_data
  <tr>
   <td class="stats_label">Schwimmteich<br />1,80 m Tiefe</td>
   <td class="stats_data">$current.extraTemp3</td>
  </tr>
#end if
  <tr><td>Sonne<br />&nbsp;</td><td>Seit dem 03.02.2017</td></tr>
  <tr>
   <td class="stats_label">Beleuchtungsstärke<br />(Illuminance)</td>
   <td class="stats_data">$current.lighting</td>
  </tr>
  <tr>
    <td class="stats_label">UV<br />&nbsp;</td>
    <!-- <td class="stats_data">$current.UV</td> -->
    <td class="stats_data" style="$decorator_color('uv', $current.UV.raw)">$current.UV 
     &nbsp;&nbsp; $decorator_text('uv', $current.UV.raw)</td>
   </tr>
   <tr>
#if $current.radiation.raw > 0.0 and $current.maxSolarRad.raw > 0.0
    #set $anteil = $current.radiation.raw * 100 / $current.maxSolarRad.raw
    #set $anteil = ("{:.2f}".format($anteil));
#else
    #set $anteil = 0.0
#end if
    <td class="stats_label">Globalstrahlung<br />&nbsp;</td>
    <td class="stats_data">$current.radiation&nbsp;(das sind&nbsp;$anteil&nbsp;% vom Maximum)</td>
   </tr>
   <tr>
    <td class="stats_label">Sonnestunden am Tag<br />Berechnung&nbsp;</td>
    <td class="stats_data">$day.sunshineS.sum.hour</td>
   </tr>
   <tr><td>1-Wire OWFS USB<br />Bodentemperatur</td><td>Seit dem 10.08.2015</td></tr>
#if $day.extraTemp7.has_data
   <tr>
    <td class="stats_label">Boden +100cm<br />&nbsp;</td>
    <td class="stats_data" style="$decorator_color('tempO', $current.extraTemp7.raw)">$current.extraTemp7</td>
   </tr>
#end if
#if $day.extraTemp5.has_data
   <tr>
    <td class="stats_label">Boden +5cm<br />&nbsp;</td>
    <td class="stats_data" style="$decorator_color('tempO', $current.extraTemp5.raw)">$current.extraTemp5</td>
   </tr>
#end if
#if $day.soilTempO1.has_data
   <tr>
    <td class="stats_label">Boden -5cm<br />&nbsp;</td>
    <td class="stats_data" style="$decorator_color('tempO', $current.soilTempO1.raw)">$current.soilTempO1</td>
   </tr>
#end if
#if $day.soilTempO2.has_data
   <tr>
    <td class="stats_label">Boden -10cm<br />&nbsp;</td>
    <td class="stats_data" style="$decorator_color('tempO', $current.soilTempO2.raw)">$current.soilTempO2</td>
   </tr>
#end if
#if $day.soilTempO3.has_data
   <tr>
    <td class="stats_label">Boden -20cm<br />&nbsp;</td>
    <td class="stats_data" style="$decorator_color('tempO', $current.soilTempO3.raw)">$current.soilTempO3</td>
   </tr>
#end if
#if $day.soilTempO4.has_data
   <tr>
    <td class="stats_label">Boden -50cm<br />&nbsp;</td>
    <td class="stats_data" style="$decorator_color('tempO', $current.soilTempO4.raw)">$current.soilTempO4</td>
   </tr>
#end if
#if $day.soilTempO5.has_data
   <tr>
    <td class="stats_label">Boden -100cm<br />&nbsp;</td>
    <td class="stats_data" style="$decorator_color('tempO', $current.soilTempO5.raw)">$current.soilTempO5</td>
   </tr>
#end if
   <tr><td>Davis<br />Bodentemperatur</td><td>Seit dem 03.02.2017</td></tr>
#if $day.soilTemp1.has_data
   <tr>
    <td class="stats_label">Boden -5cm<br />&nbsp;</td>
    <td class="stats_data" style="$decorator_color('tempO', $current.soilTemp1.raw)">$current.soilTemp1</td> 
   </tr>
#end if
#if $day.soilTemp2.has_data
   <tr>
    <td class="stats_label">Boden -10cm<br />&nbsp;</td>
    <td class="stats_data" style="$decorator_color('tempO', $current.soilTemp2.raw)">$current.soilTemp2</td>
   </tr>
#end if
#if $day.soilTemp3.has_data
   <tr>
    <td class="stats_label">Boden -20cm<br />&nbsp;</td>
    <td class="stats_data" style="$decorator_color('tempO', $current.soilTemp3.raw)">$current.soilTemp3</td>
   </tr>
#end if
#if $day.soilTemp4.has_data
   <tr>
    <td class="stats_label">Boden -50cm<br />&nbsp;</td>
    <td class="stats_data" style="$decorator_color('tempO', $current.soilTemp4.raw)">$current.soilTemp4</td>
   </tr>
#end if
   <tr><td>Davis<br />Bodenfeuchtigkeit</td><td>Seit dem 03.02.2017</td></tr>
#if $day.soilMoist1.has_data
   <tr>
    <td class="stats_label">Bodenfeuchte bei<br />-5 cm</td>
    <td class="stats_data" style="$decorator_color('soilmoist', $current.soilMoist1.raw)">$current.soilMoist1
     &nbsp; $decorator_text('soilmoist', $current.soilMoist1.raw)</td>
   </tr>
#end if
#if $day.soilMoist2.has_data
   <tr>
    <td class="stats_label">Bodenfeuchte<br />-10 cm&nbsp;</td>
    <td class="stats_data" style="$decorator_color('soilmoist', $current.soilMoist2.raw)">$current.soilMoist2
     &nbsp; $decorator_text('soilmoist', $current.soilMoist2.raw)</td>
   </tr>
#end if
#if $day.soilMoist3.has_data
   <tr>
    <td class="stats_label">Bodenfeuchte<br />-20 cm&nbsp;</td>
    <td class="stats_data" style="$decorator_color('soilmoist', $current.soilMoist3.raw)">$current.soilMoist3
     &nbsp; $decorator_text('soilmoist', $current.soilMoist3.raw)</td>
   </tr>
#end if
#if $day.soilMoist4.has_data
   <tr>
    <td class="stats_label">Bodenfeuchte<br />-50 cm&nbsp;</td>
    <td class="stats_data" style="$decorator_color('soilmoist', $current.soilMoist4.raw)">$current.soilMoist4
     &nbsp; $decorator_text('soilmoist', $current.soilMoist4.raw)</td>
   </tr>
#end if
   <tr><td>Davis<br />Blattfeuchtigkeit</td><td>Seit dem 03.02.2017</td></tr>
#if $day.leafWet1.has_data
   <tr>
    <td class="stats_label">Blattfeuchte 1<br />Blick Nord</td>
    <!-- <td class="stats_data">$current.leafWet1</td> -->
    <td class="stats_data" style="$decorator_color('leafwet', $current.leafWet1.raw)">$current.leafWet1
     &nbsp; $decorator_text('leafwet', $current.leafWet1.raw)</td>
   </tr>
#end if
#if $day.leafWet2.has_data
   <tr>
    <td class="stats_label">Blattfeuchte 2<br />Blick Süd</td>
    <!-- <td class="stats_data">$current.leafWet2</td> -->
    <td class="stats_data" style="$decorator_color('leafwet', $current.leafWet2.raw)">$current.leafWet2
     &nbsp; $decorator_text('leafwet', $current.leafWet2.raw)</td>
   </tr>
#end if
   <tr>
    <td>Station<br /> Büro</td><td>Server</td>
   </tr>
   <tr>
    <td class="stats_label">Temperatur <sup>(innen)</sup><br />&nbsp;</td>
    <td class="stats_data">$current.inTemp</td>
   </tr>
   <tr>
     <td class="stats_label">Luftfeuchte <sup>(innen)</sup><br />&nbsp;</td>
     <td class="stats_data">$current.inHumidity</td>
   </tr>
   <tr>
     <td class="stats_label">Taupunkt <sup>(innen)</sup><br />&nbsp;</td>
     <td class="stats_data">$current.inDewpoint</td>
   </tr>
   <tr>
     <td class="stats_label">tatsächliche Dampfdichte <sup>(innen)</sup><br />&nbsp;</td>
     <td class="stats_data">$latest($data_binding='wd_binding').AVPin</td>
   </tr>
   <tr>
     <td class="stats_label">Sättigungsdampfdichte <sup>(innen)</sup><br />&nbsp;</td>
     <td class="stats_data">$latest($data_binding='wd_binding').SVPin</td>
   </tr>

   <tr><td>Strahlung<br />Radiaktivität</td><td>Seit dem 15.12.2017</td></tr>
   <tr>
     <td class="stats_label">Zerfall je Minute<br />&nbsp;</td>
     <td class="stats_data" style="$decorator_color('cpm', $latest($data_binding='geiger_binding').rad_cpm.raw)">
      $latest($data_binding='geiger_binding').rad_cpm.format("%.1f")
      &nbsp;&nbsp; $decorator_text('cpm', $latest($data_binding='geiger_binding').rad_cpm.raw)</td>
     <!-- <td class="stats_data">$latest($data_binding='geiger_binding').rad_cpm.format("%.0f")&nbsp;CPM</td> -->
   </tr>
   <tr>
     <td class="stats_label">Radioaktivität<br />&nbsp;</td>
     <td class="stats_data" style="$decorator_color('msvh', $latest($data_binding='geiger_binding').rad_nsvh.raw)">
      $latest($data_binding='geiger_binding').rad_nsvh
      &nbsp;&nbsp; $decorator_text('msvh', $latest($data_binding='geiger_binding').rad_nsvh.raw)</td>
     <!-- <td class="stats_data">$latest($data_binding='geiger_binding').rad_nsvh</td> -->
   </tr>
   <tr><td>Berechnungen<br />weewx</td><td>Info</td></tr>
   <tr>
    <td class="stats_label">Density altitude<br />Dichtehöhe</td>
    <td>$current.densityA</td>
   </tr>
   <tr>
    <td class="stats_label">Wolkenuntergrenze<br />&nbsp;</td>
    <td>$current.cloudbase</td>
   </tr>
   <tr>
    <td class="stats_label">Summer-Simmer-Index
     <div class="popup" onclick="myFunction()"> <sup>( Info )</sup>
      <span class="popuptext" id="myPopup">Der Summer-Simmer-Index bezieht sich im Vergleich zum Hitzeindex auf die gefühlte Hitze<br />
                                           in der Nacht und stellt einen Fraktor für das Unwohlsein dar. <br />
                                           Er findet ab 22°C Anwendung.</span></div>
    <br />&nbsp;</td>
    <!-- <td class="stats_data"><b>$current.summersimmerIndex</b></td> -->
    <td class="stats_data" style="$decorator_color('sumsimIndex', $current.summersimmerIndex.raw)">$current.summersimmerIndex
     &nbsp; $decorator_text('sumsimIndex', $current.summersimmerIndex.raw)</td>
   </tr>
   <tr>
    <td class="stats_label">Wachstumstage Monat<br />&nbsp;</td>
    <td>$month.outTemp.max_ge((10.0, "degree_C", "group_temperature")).format("%.0f")</td>
   </tr>
   <tr>
    <td class="stats_label">Wachstumstage Jahr<br />&nbsp;</td>
    <td>$year.outTemp.max_ge((10.0, "degree_C", "group_temperature")).format("%.0f")</td>
   </tr>
   <tr>
    <td class="stats_label">Heiztage im Monat<br />&nbsp;</td>
    <td>$month.outTemp.max_le((15.0, "degree_C", "group_temperature")).format("%.0f")</td>
   </tr>
   <tr>
    <td class="stats_label">Heiztage im Jahr<br />&nbsp;</td>
    <td>$year.outTemp.max_le((15.0, "degree_C", "group_temperature")).format("%.0f")</td>
   </tr>
   <tr>
     <td class="stats_label">Masszahl für den Wärmebedarfs<br /> eine Gebäudes. Basis 18 °C.</td>
     <td>$day.heatdeg.sum</td>
   </tr>
   <tr>
     <td class="stats_label">Masszahl zur Kühlung <br />eines Gebäudes. Basis 18 °C</td>
     <td>$day.cooldeg.sum</td>
   </tr>
   <tr>
     <td class="stats_label">Heizgradtag <br />eines Gebäudes. Basis 15 °C</td>
     <td>$latest($data_binding='wd_binding').homedeg</td>
   </tr>
   <tr>
    <td class="stats_label">Kühlgrenztemperatur<br />Feuchte Kugel Temperatur</td>
    <!-- <td>$current.wetBulb </td> -->
    <td class="stats_data" style="$decorator_color('wetBulb', $current.wetBulb.raw)">$current.wetBulb
     &nbsp; $decorator_text('wetBulb', $current.wetBulb.raw)</td>
   </tr>
   <tr>
    <td class="stats_label">Brandgefahr-<br />Index</td>
    <!-- <td>$current.cbIndex&nbsp;/&nbsp;100</td> -->
    <td class="stats_data" style="$decorator_color('cbIndex', $current.cbIndex.raw)">$current.cbIndex&nbsp;/100
     &nbsp; $decorator_text('cbIndex', $current.cbIndex.raw)</td>
   </tr>
   <tr><td>Davis Vantage Pro 2<br />Modell 6163EU</td><td>Seit dem 20.06.2016</td></tr>
   <tr>
    <td class="stats_label">SenderBatterie<br />&nbsp;</td>
   #if $current.txBatteryStatus.raw == 0
       <td><font color='blue'>i.O.</font></td>
   #else
       <td><font color='red'>Null</font></td>
   #end if
   </tr>
   <tr>
    <td class="stats_label">Stationsspannung<br />&nbsp;</td>
    <td>$current.consBatteryVoltage</td>
   </tr>
   <tr>
    <td class="stats_label">Signal<br />&nbsp;</td>
    <!-- <td>$current.rxCheckPercent</td> -->
    <td class="stats_data" style="$decorator_color('empfang', $current.rxCheckPercent.raw)">$current.rxCheckPercent
     &nbsp; $decorator_text('empfang', $current.rxCheckPercent.raw)</td>
   </tr>
   <tr><td>1-Wire OWFS USB<br />Volt</td><td>Seit dem 10.08.2015</td></tr>
   <tr>
    <td class="stats_label">USB-Volt<br />&nbsp;</td>
    <td>$current.heatingVoltage</td>
   </tr>
   <tr>
    <td class="stats_label">Hum-Volt<br />&nbsp;</td>
    <td>$current.supplyVoltage</td>
   </tr>
   <tr>
    <td class="stats_label">Son-Volt<br />&nbsp;</td>
    <td>$current.referenceVoltage</td>
   </tr>
  </tbody>
 </table>
</div>
<p>&nbsp;</p><!-- End current -->


#encoding UTF-8
## chart.inc  2015-02-23 18:24:18Z hes $
<div class="stats">
 <div class="stats_header">
  Werte für
 </div>
 <table>
  <tbody>
   <tr>
    <td class="stats"></td>
    <td class="stats_header">$period1Name</td>
    <td class="stats_header">$period2Name</td>
   </tr>
   <tr>
    <td class="stats_label">Temperatur (max) / (min)</td>
<td class="stats_data">
  $period1.outTemp.max um $period1.outTemp.maxtime<br/>
  $period1.outTemp.min um $period1.outTemp.mintime
</td>
<td class="stats_data">
  $period2.outTemp.max um $period2.outTemp.maxtime<br/>
  $period2.outTemp.min um $period2.outTemp.mintime
</td>
</tr>
<tr>
<td class="stats_label">
  scheinbare (max)<br />
  Temperatur (min)
</td>
<td class="stats_data">
  $period1.appTemp.max um $period1.appTemp.maxtime<br/>
  $period1.appTemp.min um $period1.appTemp.mintime
</td>
<td class="stats_data">
  $period2.appTemp.max um $period2.appTemp.maxtime<br/>
  $period2.appTemp.min um $period2.appTemp.mintime
</td>
</tr>
<tr>
<td class="stats_label">  Hitzeindex (max)<br /> &nbsp;</td>
<td class="stats_data">
  $period1.heatindex.max um $period1.heatindex.maxtime
</td>
<td class="stats_data">
  $period2.heatindex.max um $period2.heatindex.maxtime
</td>
</tr>
<tr>
<td class="stats_label">  Windchill  (min)<br /> &nbsp;</td>
<td class="stats_data">
  $period1.windchill.min um $period1.windchill.mintime
</td>
<td class="stats_data">
  $period2.windchill.min um $period2.windchill.mintime
</td>
</tr>
<tr>
<td class="stats_label">  Taupunkt (max) / (min)</td>
<td class="stats_data">
  $period1.dewpoint.max um $period1.dewpoint.maxtime<br />
  $period1.dewpoint.min um $period1.dewpoint.mintime
</td>
<td class="stats_data">
  $period2.dewpoint.max um $period2.dewpoint.maxtime<br />
  $period2.dewpoint.min um $period2.dewpoint.mintime
</td>
</tr>
<tr>
<td class="stats_label">  Luftfeuchte (max) / (min)</td>
<td class="stats_data">
  $period1.outHumidity.max um $period1.outHumidity.maxtime<br />
  $period1.outHumidity.min um $period1.outHumidity.mintime
</td>
<td class="stats_data">
  $period2.outHumidity.max um $period2.outHumidity.maxtime<br />
  $period2.outHumidity.min um $period2.outHumidity.mintime
</td>
</tr>
<tr>
<td class="stats_label">  
      absolute&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;(max)<br />
      Luftfeuchte (min)
</td>
<td class="stats_data">
  $period1.absolutF.max um $period1.absolutF.maxtime<br />
  $period1.absolutF.min um $period1.absolutF.mintime
</td>
<td class="stats_data">
  $period2.absolutF.max um $period2.absolutF.maxtime<br />
  $period2.absolutF.min um $period2.absolutF.mintime
</td>
</tr>
<tr>
<td class="stats_label">  Luftdruck (max) / (min)</td>
<td class="stats_data">
  $period1.barometer.max um $period1.barometer.maxtime<br />
  $period1.barometer.min um $period1.barometer.mintime
</td>
<td class="stats_data">
  $period2.barometer.max um $period2.barometer.maxtime<br />
  $period2.barometer.min um $period2.barometer.mintime
</td>
</tr>
<tr>
<td class="stats_label">Luftdichte (max) / (min)</td>
<td class="stats_data">
  $period1.airDensity.max um $period1.airDensity.maxtime<br />
  $period1.airDensity.min um $period1.airDensity.mintime
</td>
<td class="stats_data">
  $period2.airDensity.max um $period2.airDensity.maxtime<br />
  $period2.airDensity.min um $period2.airDensity.mintime
</td>
</tr>
<tr>
<td class="stats_label">Regen (gesamt)<br /> &nbsp;</td>
<td class="stats_data">$period1.rain.sum</td>
<td class="stats_data">$period2.rain.sum</td>
</tr>
<tr>
<td class="stats_label">Regenintensität (max)<br /> &nbsp;</td>
<td class="stats_data">$period1.rainRate.max um $period1.rainRate.maxtime</td>
<td class="stats_data">$period2.rainRate.max um $period2.rainRate.maxtime</td>
</tr>
<tr>
<td class="stats_label">Schneehöhe (gesamt)<br /> &nbsp;</td>
<td class="stats_data">$period1.snowTotal.max um $period1.snowTotal.maxtime</td>
<td class="stats_data">$period2.snowTotal.max um $period2.snowTotal.maxtime</td>
</tr>
<tr>
<td class="stats_label"> ET  (sum)<br /> &nbsp; </td>
<td class="stats_data">
  $period1.ET.sum
</td>
<td class="stats_data">
  $period2.ET.sum
</td>
</tr>
<tr>
<td class="stats_label"> Windgeschwindigkeit<br />Böe</td>
<td class="stats_data">
  $period1.windGust.max aus $period1.wind.gustdir ($period1.wind.gustdir.ordinal_compass)
  <br />um $period1.windGust.maxtime
</td>
<td class="stats_data">
  $period2.windGust.max aus $period2.wind.gustdir ($period2.wind.gustdir.ordinal_compass)
  <br />um $period2.windGust.maxtime
</td>
</tr>
<tr>
<td class="stats_label"> Windgeschwindigkeit<br />Wind</td>
<td class="stats_data">
  $period1.windSpeed.max aus $period1.wind.gustdir ($period1.wind.gustdir.ordinal_compass)
  <br />um $period1.windSpeed.maxtime
</td>
<td class="stats_data">
  $period2.windSpeed.max aus $period2.wind.gustdir ($period2.wind.gustdir.ordinal_compass)
  <br />um $period2.windSpeed.maxtime
</td>
</tr>
<!-- <tr>
<td class="stats_label"> Windgeschwindigkeit<br />&nbsp;</td>
<td class="stats_data">
  $period1.wind.max aus $period1.wind.gustdir ($period1.wind.gustdir.ordinal_compass)
  <br />um $period1.wind.maxtime
</td>
<td class="stats_data">
  $period2.wind.max aus $period2.wind.gustdir ($period2.wind.gustdir.ordinal_compass)
  <br />um $period2.wind.maxtime
</td>
</tr> -->
<tr>
<td class="stats_label">  Windgeschwindigkeit &Oslash;<br />&nbsp;</td>
<td class="stats_data">
  $period1.wind.avg
</td>
<td class="stats_data">
  $period2.wind.avg
</td>
</tr>
<tr>
<td class="stats_label">  RMS Wind<br />&nbsp;</td>
<td class="stats_data">
  $period1.wind.rms
</td>
<td class="stats_data">
  $period2.wind.rms
</td>
</tr>
<tr>
<td class="stats_label">
  &Oslash; Geschwindigkeit<br />
  &Oslash; Himmelsrichtung 
</td>
<td class="stats_data">
  $period1.wind.vecavg<br />
  $period1.wind.vecdir ($period1.wind.vecdir.ordinal_compass)
</td>
<td class="stats_data">
  $period2.wind.vecavg<br />
  $period2.wind.vecdir ($period2.wind.vecdir.ordinal_compass)
</td>
</tr>
<tr>
<td class="stats_label">  Winddruck<br /> &nbsp;</td>
<td class="stats_data">
  $period1.windDruck.max um $period1.windDruck.maxtime
</td>
<td class="stats_data">
  $period2.windDruck.max um $period2.windDruck.maxtime
</td>
</tr>
<tr><td colspan="3">1-Wire  OWFS USB Wassertemperatur</td></tr>
#if $period1.extraTemp1.has_data
<tr>
<td class="stats_label">Teich 0,75 m³ (max) / (min) </td>
<td class="stats_data">
  $period1.extraTemp1.max um $period1.extraTemp1.maxtime<br />
  $period1.extraTemp1.min um $period1.extraTemp1.mintime
</td>
<td class="stats_data">
  $period2.extraTemp1.max um $period2.extraTemp1.maxtime<br />
  $period2.extraTemp1.min um $period2.extraTemp1.mintime
</td>
</tr>
#end if
#if $period1.extraTemp2.has_data
<tr>
<td class="stats_label">Teich 96 m³ (max) / (min) </td>
<td class="stats_data">
  $period1.extraTemp2.max um $period1.extraTemp2.maxtime<br />
  $period1.extraTemp2.min um $period1.extraTemp2.mintime
</td>
<td class="stats_data">
  $period2.extraTemp2.max um $period2.extraTemp2.maxtime<br />
  $period2.extraTemp2.min um $period2.extraTemp2.mintime
</td>
</tr>
#end if
#if $period1.extraTemp3.has_data
<tr>
<td class="stats_label">Teich 96 m³ Grund (max) / (min) </td>
<td class="stats_data">
  $period1.extraTemp3.max um $period1.extraTemp3.maxtime<br />
  $period1.extraTemp3.min um $period1.extraTemp3.mintime
</td>
<td class="stats_data">
  $period2.extraTemp3.max um $period2.extraTemp3.maxtime<br />
  $period2.extraTemp3.min um $period2.extraTemp3.mintime
</td>
</tr>
#end if
#if $period1.extraTemp6.has_data
<tr>
<td class="stats_label">Teich 22 m³ (max) / (min) </td>
<td class="stats_data">
  $period1.extraTemp6.max um $period1.extraTemp6.maxtime<br />
  $period1.extraTemp6.min um $period1.extraTemp6.mintime
</td>
<td class="stats_data">
  $period2.extraTemp6.max um $period2.extraTemp6.maxtime<br />
  $period2.extraTemp6.min um $period2.extraTemp6.mintime
</td>
</tr>
#end if
<tr><td colspan="3">Davis Temperatur</td></tr>
#if $period1.leafTemp1.has_data
<tr>
<td class="stats_label">Teichfilter Zulauf</td>
<td class="stats_data">
  $period1.leafTemp1.max um $period1.leafTemp1.maxtime<br />
  $period1.leafTemp1.min um $period1.leafTemp1.mintime
</td>
<td class="stats_data">
  $period2.leafTemp1.max um $period2.leafTemp1.maxtime<br />
  $period2.leafTemp1.min um $period2.leafTemp1.mintime
</td>
</tr>
#end if
#if $period1.leafTemp2.has_data
<tr>
<td class="stats_label">Teichfilter Ablauf</td>
<td class="stats_data">
  $period1.leafTemp2.max um $period1.leafTemp2.maxtime<br />
  $period1.leafTemp2.min um $period1.leafTemp2.mintime
</td>
<td class="stats_data">
  $period2.leafTemp2.max um $period2.leafTemp2.maxtime<br />
  $period2.leafTemp2.min um $period2.leafTemp2.mintime
</td>
</tr>
#end if
<tr><td colspan="3">1-Wire  OWFS USB Temperatur</td></tr>
#if $period1.extraTemp4.has_data
<tr>
<td class="stats_label">  Carport (max) / (min) </td>
<td class="stats_data">
  $period1.extraTemp4.max um $period1.extraTemp4.maxtime<br />
  $period1.extraTemp4.min um $period1.extraTemp4.mintime
</td>
<td class="stats_data">
  $period2.extraTemp4.max um $period2.extraTemp4.maxtime<br />
  $period2.extraTemp4.min um $period2.extraTemp4.mintime
</td>
</tr>
#end if

#if $period1.extraTemp8.has_data
<tr>
<td class="stats_label">  Schwimmsteg (max) / (min) </td>
<td class="stats_data">
  $period1.extraTemp8.max um $period1.extraTemp8.maxtime<br />
  $period1.extraTemp8.min um $period1.extraTemp8.mintime
</td>
<td class="stats_data">
  $period2.extraTemp8.max um $period2.extraTemp8.maxtime<br />
  $period2.extraTemp8.min um $period2.extraTemp8.mintime
</td>
</tr>
#end if
<tr><td colspan="3">Davis Sonne</td></tr>
#if $period1.lighting.has_data
<tr>
<td class="stats_label">
  Beleuchtungsstärke (max)<br />&nbsp;Illuminance
</td>
<td class="stats_data">
  $period1.lighting.max um $period1.lighting.maxtime
</td>
<td class="stats_data">
  $period2.lighting.max um $period2.lighting.maxtime
</td>
</tr>
#end if

#if $period1.radiation.has_data
<tr>
<td class="stats_label">  Globalstrahlung (max)<br />&nbsp;&nbsp;</td>
<td class="stats_data">
  $period1.radiation.max um $period1.radiation.maxtime
</td>
<td class="stats_data">
  $period2.radiation.max um $period2.radiation.maxtime
</td>
</tr>
<tr>
<td class="stats_label">  Globalstrahlung Summe<br /> &nbsp;</td>
<td class="stats_data">
  $period1.radiation.sum
</td>
<td class="stats_data">
  $period2.radiation.sum
</td>
</tr>
#end if
#if $period1.sunshineS.has_data
<tr>
<td class="stats_label">  Sonnenscheindauer (max)<br /> &nbsp;</td>
<td class="stats_data">
  $period1.sunshineS.sum.hour 
</td>
<td class="stats_data">
  $period2.sunshineS.sum.hour
</td>
</tr>
#end if
#if $period1.UV.has_data
<tr>
<td class="stats_label">UV-Index (max)<br /> &nbsp;</td>
<td class="stats_data">
  $period1.UV.max
</td>
<td class="stats_data">
  $period2.UV.max
</td>
</tr>
#end if
<tr><td colspan="3">1-Wire  OWFS USB Lufttemperatur</td></tr>
#if $period1.extraTemp7.has_data
<tr>
<td class="stats_label">
  bei 100 cm (max) / (min)
</td>
<td class="stats_data">
  $period1.extraTemp7.max um $period1.extraTemp7.maxtime<br />
  $period1.extraTemp7.min um $period1.extraTemp7.mintime
</td>
<td class="stats_data">
  $period2.extraTemp7.max um $period2.extraTemp7.maxtime<br />
  $period2.extraTemp7.min um $period2.extraTemp7.mintime
</td>
</tr>
#end if
#if $period1.extraTemp5.has_data
<tr>
<td class="stats_label">
  bei 5 cm (max) / (min)
</td>
<td class="stats_data">
  $period1.extraTemp5.max um $period1.extraTemp5.maxtime<br />
  $period1.extraTemp5.min um $period1.extraTemp5.mintime
</td>
<td class="stats_data">
  $period2.extraTemp5.max um $period2.extraTemp5.maxtime<br />
  $period2.extraTemp5.min um $period2.extraTemp5.mintime
</td>
</tr>
#end if
<tr><td colspan="3">1-Wire  OWFS USB Bodentemperatur</td></tr>
#if $period1.soilTempO1.has_data
<tr>
<td class="stats_label">bei -5 cm (max) / (min)
</td>
<td class="stats_data">
  $period1.soilTempO1.max um $period1.soilTempO1.maxtime<br />
  $period1.soilTempO1.min um $period1.soilTempO1.mintime
</td>
<td class="stats_data">
  $period2.soilTempO1.max um $period2.soilTempO1.maxtime<br />
  $period2.soilTempO1.min um $period2.soilTempO1.mintime
</td>
</tr>
#end if

#if $period1.soilTempO2.has_data
<tr>
<td class="stats_label">bei -10 cm (max) / (min)
</td>
<td class="stats_data">
  $period1.soilTempO2.max um $period1.soilTempO2.maxtime<br />
  $period1.soilTempO2.min um $period1.soilTempO2.mintime
</td>
<td class="stats_data">
  $period2.soilTempO2.max um $period2.soilTempO2.maxtime<br />
  $period2.soilTempO2.min um $period2.soilTempO2.mintime
</td>

</tr>
#end if

#if $period1.soilTempO3.has_data
<tr>
<td class="stats_label">bei -20 cm (max) / (min)
</td>
<td class="stats_data">
  $period1.soilTempO3.max um $period1.soilTempO3.maxtime<br />
  $period1.soilTempO3.min um $period1.soilTempO3.mintime
</td>
<td class="stats_data">
  $period2.soilTempO3.max um $period2.soilTempO3.maxtime<br />
  $period2.soilTempO3.min um $period2.soilTempO3.mintime
</td>
</tr>
#end if

#if $period1.soilTempO4.has_data
<tr>
<td class="stats_label">bei -50 cm (max) / (min)
</td>
<td class="stats_data">
  $period1.soilTempO4.max um $period1.soilTempO4.maxtime<br />
  $period1.soilTempO4.min um $period1.soilTempO4.mintime
</td>
<td class="stats_data">
  $period2.soilTempO4.max um $period2.soilTempO4.maxtime<br />
  $period2.soilTempO4.min um $period2.soilTempO4.mintime
</td>
</tr>
#end if

#if $period1.soilTempO5.has_data
<tr>
<td class="stats_label">bei -100 cm (max) / (min)
</td>
<td class="stats_data">
  $period1.soilTempO5.max um $period1.soilTempO5.maxtime<br />
  $period1.soilTempO5.min um $period1.soilTempO5.mintime
</td>
<td class="stats_data">
  $period2.soilTempO5.max um $period2.soilTempO5.maxtime<br />
  $period2.soilTempO5.min um $period2.soilTempO5.mintime
</td>
</tr>
#end if
#if $period2.soilTemp2.has_data
<tr><td colspan="3">Davis Bodentemperatur </td></tr>
#if $period1.soilTemp1.has_data
<tr>
<td class="stats_label">bei -5 cm (max) / (min)
</td>
<td class="stats_data">
  $period1.soilTemp1.max um $period1.soilTemp1.maxtime<br />
  $period1.soilTemp1.min um $period1.soilTemp1.mintime
</td>
<td class="stats_data">
  $period2.soilTemp1.max um $period2.soilTemp1.maxtime<br />
  $period2.soilTemp1.min um $period2.soilTemp1.mintime
</td>
</tr>
#end if
#if $period1.soilTemp2.has_data
<tr>
<td class="stats_label">bei -10 cm (max) / (min)
</td>
<td class="stats_data">
  $period1.soilTemp2.max um $period1.soilTemp2.maxtime<br />
  $period1.soilTemp2.min um $period1.soilTemp2.mintime
</td>
<td class="stats_data">
  $period2.soilTemp2.max um $period2.soilTemp2.maxtime<br />
  $period2.soilTemp2.min um $period2.soilTemp2.mintime
</td>
</tr>
#end if
#if $period1.soilTemp3.has_data
<tr>
<td class="stats_label">bei -20 cm (max) / (min)
</td>
<td class="stats_data">
  $period1.soilTemp3.max um $period1.soilTemp3.maxtime<br />
  $period1.soilTemp3.min um $period1.soilTemp3.mintime
</td>
<td class="stats_data">
  $period2.soilTemp3.max um $period2.soilTemp3.maxtime<br />
  $period2.soilTemp3.min um $period2.soilTemp3.mintime
</td>
</tr>
#end if
#if $period1.soilTemp4.has_data
<tr>
<td class="stats_label">bei -50 cm (max) / (min)
</td>
<td class="stats_data">
  $period1.soilTemp4.max um $period1.soilTemp4.maxtime<br />
  $period1.soilTemp4.min um $period1.soilTemp4.mintime
</td>
<td class="stats_data">
  $period2.soilTemp4.max um $period2.soilTemp4.maxtime<br />
  $period2.soilTemp4.min um $period2.soilTemp4.mintime
</td>
</tr>
#end if
<tr><td colspan="3">Davis Bodenfeuchte</td></tr>
#if $period1.soilMoist1.has_data
<tr>
<td class="stats_label">bei -5 cm (max) / (min)</td>
<td class="stats_data">
  $period1.soilMoist1.max um $period1.soilMoist1.maxtime<br />
  $period1.soilMoist1.min um $period1.soilMoist1.mintime
</td>
<td class="stats_data">
  $period2.soilMoist1.max um $period2.soilMoist1.maxtime<br />
  $period2.soilMoist1.min um $period2.soilMoist1.mintime
</td>
</tr>
#end if

#if $period1.soilMoist2.has_data
<tr>
<td class="stats_label">bei -10 cm (max) / (min)
</td>
<td class="stats_data">
  $period1.soilMoist2.max um $period1.soilMoist2.maxtime<br />
  $period1.soilMoist2.min um $period1.soilMoist2.mintime
</td>
<td class="stats_data">
  $period2.soilMoist2.max um $period2.soilMoist2.maxtime<br />
  $period2.soilMoist2.min um $period2.soilMoist2.mintime
</td>
</tr>
#end if

#if $period1.soilMoist3.has_data
<tr>
<td class="stats_label">bei -20 cm (max) / (min)
</td>
<td class="stats_data">
  $period1.soilMoist3.max um $period1.soilMoist3.maxtime<br />
  $period1.soilMoist3.min um $period1.soilMoist3.mintime
</td>
<td class="stats_data">
  $period2.soilMoist3.max um $period2.soilMoist3.maxtime<br />
  $period2.soilMoist3.min um $period2.soilMoist3.mintime
</td>
</tr>
#end if

#if $period1.soilMoist4.has_data
<tr>
<td class="stats_label">bei -50 cm (max) / (min)
</td>
<td class="stats_data">
  $period1.soilMoist4.max um $period1.soilMoist4.maxtime<br />
  $period1.soilMoist4.min um $period1.soilMoist4.mintime
</td>
<td class="stats_data">
  $period2.soilMoist4.max um $period2.soilMoist4.maxtime<br />
  $period2.soilMoist4.min um $period2.soilMoist4.mintime
</td>
</tr>
#end if
<tr><td colspan="3">Davis Blattfeuchte</td></tr>
#if $period1.leafWet1.has_data
<tr>
<td class="stats_label">Nord (max) / (min)</td>
<td class="stats_data">
  $period1.leafWet1.max um $period1.leafWet1.maxtime<br />
  $period1.leafWet1.min um $period1.leafWet1.mintime
</td>
<td class="stats_data">
  $period2.leafWet1.max um $period2.leafWet1.maxtime<br />
  $period2.leafWet1.min um $period2.leafWet1.mintime
</td>
</tr>
#end if
#if $period1.leafWet2.has_data
<tr>
<td class="stats_label"> Süd (max) / (min)
</td>
<td class="stats_data">
  $period1.leafWet2.max um $period1.leafWet2.maxtime<br />
  $period1.leafWet2.min um $period1.leafWet2.mintime
</td>
<td class="stats_data">
  $period2.leafWet2.max um $period2.leafWet2.maxtime<br />
  $period2.leafWet2.min um $period2.leafWet2.mintime
</td>
</tr>
#end if
#end if
<tr>
<td colspan="3">Station Büro Info</td>
</tr>
<tr>
<td class="stats_label">  Temperatur (max) / (min)</td>
<td class="stats_data">
  $period1.inTemp.max um $period1.inTemp.maxtime<br />
  $period1.inTemp.min um $period1.inTemp.mintime
</td>
<td class="stats_data">
  $period2.inTemp.max um $period2.inTemp.maxtime<br />
  $period2.inTemp.min um $period2.inTemp.mintime
</td>
</tr>
<tr>
<td class="stats_label">  Luftfeuchte (max) / (min)
</td>
<td class="stats_data">
  $period1.inHumidity.max um $period1.inHumidity.maxtime<br />
  $period1.inHumidity.min um $period1.inHumidity.mintime
</td>
<td class="stats_data">
  $period2.inHumidity.max um $period2.inHumidity.maxtime<br />
  $period2.inHumidity.min um $period2.inHumidity.mintime
</td>
 </tr>
<tr>
<td class="stats_label"> Taupunkt (max) / (min)
</td>
<td class="stats_data">
  $period1.inDewpoint.max um $period1.inDewpoint.maxtime<br />
  $period1.inDewpoint.min um $period1.inDewpoint.mintime
</td>
<td class="stats_data">
  $period2.inDewpoint.max um $period2.inDewpoint.maxtime<br />
  $period2.inDewpoint.min um $period2.inDewpoint.mintime
</td>
 </tr>
 
<tr><td colspan="3">Berechnung in weewx</td></tr>
<tr><td>Wolkenuntergrenze<br />&nbsp;</td>
 <td>$period1.cloudbase.max</td>
 <td>$period2.cloudbase.max</td>
</tr>
<tr><td>Windweg<br />&nbsp;</td>
    <td>$period1.windrun.sum</td>
    <td>$period2.windrun.sum</td></tr>
<tr><td>Theoretische max <br />&nbsp;Sonnenstrahlung</td>
    <td>$period1.maxSolarRad.max</td>
    <td>$period2.maxSolarRad.max</td></tr>
<tr><td>HUM-Index<br />&nbsp;</td>
    <td>$period1.humidex.max</td>
    <td>$period2.humidex.max</td></tr>
<tr><td>Wind<br />in Beaufort</td>
    <td>$period1.windSpeed.max.beaufort</td>
    <td>$period2.windSpeed.max.beaufort</td></tr>
<tr><td>Böe<br />in Beaufort</td>
    <td>$period1.windGust.max.beaufort</td>
    <td>$period2.windGust.max.beaufort</td></tr>
  </tbody>
 </table>
</div> <!--End class "stats" -->


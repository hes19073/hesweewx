#encoding UTF-8
## hes: current.inc  2015-02-23 18:24:18Z hes $
##Wet bulb calculations
##
#try
    #set $Tc = $current.outTemp.raw
    #set $RH = $current.outHumidity.raw
    #set $P = $current.pressure.raw
    #set $Tdc = (($Tc - (14.55 + 0.114 * $Tc) * (1 - (0.01 * $RH)) - ((2.5 + 0.007 * $Tc) * (1 - (0.01 * $RH))) ** 3 - (15.9 + 0.117 * $Tc) * (1 - (0.01 * $RH)) ** 14))
    #set $E = (6.11 * 10 ** (7.5 * $Tdc / (237.7 + $Tdc)))
    #set $WBc = (((0.00066 * $P) * $Tc) + ((4098 * $E) / ((Tdc + 237.7) ** 2) * $Tdc)) / ((0.00066 * $P) + (4098 * $E) / (($Tdc + 237.7) ** 2))
    #set $WB = $WBc
    #set $WB = "%.2f °C" % $WB
#except
    #set $WB = '0'
#end try
##End Wet bulb calculations


<div class="stats">
 <div class="stats_header">
      Aktuelle Werte
 </div>
 <table>
  <tbody>
   <tr>
    <td class="stats_label">Temperatur<br />&nbsp;</td>
  #if $current.outTemp.raw < 0
    <td class="stats_data" style="background-color: limegreen">$current.outTemp</td>
  #else     
    <td class="stats_data">$current.outTemp</td>
  #end if
   </tr>
   <tr>
    <td class="stats_label">scheinbare<br />Temperatur</td>
  #if $current.appTemp.raw < 0
    <td class="stats_data" style="background-color: limegreen">$current.appTemp</td>
  #else
    <td class="stats_data">$current.appTemp</td>
  #end if
   </tr>
   <tr>
    <td class="stats_label">Windchill<br />&nbsp;</td>
  #if $current.windchill.raw < 0
    <td class="stats_data" style="background-color: limegreen">$current.windchill</td>
  #else
    <td class="stats_data">$current.windchill</td>
  #end if
   </tr>
   <tr>
    <td class="stats_label">Hitzeindex<br />&nbsp;</td>
  #if $current.heatindex.raw < 0
    <td class="stats_data" style="background-color: limegreen">$current.heatindex</td>
  #else
    <td class="stats_data">$current.heatindex</td>
  #end if
   </tr>
   <tr>
   <td class="stats_label">Taupunkt<br />&nbsp;</td>
  #if $current.dewpoint.raw < 0
   <td class="stats_data" style="background-color: limegreen">$current.dewpoint</td>
  #else
   <td class="stats_data">$current.dewpoint</td>
  #end if
   </tr>
   <tr>
    <td class="stats_label">Luftfeuchte<br />&nbsp;</td>
    <td class="stats_data">$current.outHumidity</td>
   </tr>
  #if $day.extraHumid1.has_data
   <tr>
    <td class="stats_label">Luftfeuchte 2. Messstelle<br />&nbsp;</td>
    <td class="stats_data">$current.extraHumid1</td>
   </tr>
  #end if
  #if $day.extraHumid2.has_data
   <tr>
    <td class="stats_label">Luftfeuchte 3. Messstelle<br />&nbsp;</td>
    <td class="stats_data">$current.extraHumid2</td>
   </tr>
  #end if
   <tr>
    <td class="stats_label">Luftdruck<br />&nbsp;</td>
    <td class="stats_data">$current.barometer</td>
   </tr>
   <tr>
    <td class="stats_label">Luftdruck trend ($trend.time_delta.hour.format("%.0f"))<br />&nbsp;</td>
    <td class="stats_data">$trend.barometer</td>
   </tr>
   <tr>
    <td class="stats_label">Wind<br />&nbsp;</td>
    <td class="stats_data">$current.windSpeed aus $current.windDir ($current.windDir.ordinal_compass)</td>
   </tr>
   <tr>
    <td class="stats_label">Wind in Beaufort<br />&nbsp;</td>
   #if $current.windSpeed.raw < 2
    <td class="stats_data" style="background-color: #ffffff;">0<br />Windstille</td>
   #else if $current.windSpeed.raw >= 2 and $current.windSpeed.raw < 6
    <td class="stats_data" style="background-color: #d4d4fa;">1<br />leiser Zug</td>
   #else if $current.windSpeed.raw >= 6 and $current.windSpeed.raw < 12
    <td class="stats_data" style="background-color: #bcbcfa;">2<br />leichte Brise</td>
   #else if $current.windSpeed.raw >= 12 and $current.windSpeed.raw < 20
    <td class="stats_data" style="background-color: #a4a4f8;">3<br />schwache Brise</td>
   #else if $current.windSpeed.raw >= 20 and $current.windSpeed.raw < 29
    <td class="stats_data" style="background-color: #8d8df6;">4<br />mäßige Brise</td>
   #else if $current.windSpeed.raw >= 29 and $current.windSpeed.raw < 39
    <td class="stats_data" style="background-color: #7575f2;">5<br />frische Brise</td>
   #else if $current.windSpeed.raw >= 39 and $current.windSpeed.raw < 50
    <td class="stats_data" style="background-color: #6363f0;">6<br />starker Wind</td>
   #else if $current.windSpeed.raw >= 50 and $current.windSpeed.raw < 62
    <td class="stats_data" style="background-color: #5252ed;">7<br />steifer Wind</td>
   #else if $current.windSpeed.raw >= 62 and $current.windSpeed.raw < 75
    <td class="stats_data" style="background-color: #4646eb;">8<br />stürmischer Wind</td>
   #else if $current.windSpeed.raw >= 75 and $current.windSpeed.raw < 89
    <td class="stats_data" style="background-color: #3838e8; color: #ffffff;">9<br />Sturm</td>
   #else if $current.windSpeed.raw >= 89 and $current.windSpeed.raw < 103
    <td class="stats_data" style="background-color: #2929e5; color: #ffffff;">10<br />schwerer Sturm</td>
   #else if $current.windSpeed.raw >= 103 and $current.windSpeed.raw < 117
    <td class="stats_data" style="background-color: #1616e3; color: #ffffff;">11<br />orkanartiger Sturm</td>
   #else if $current.windSpeed.raw >= 117
    <td class="stats_data" style="background-color: #000000; color: #ffffff;">12<br />Orkan</td>
   #end if
   </tr>
   <tr>
    <td class="stats_label">Niederschlag,<br>der letzten 5 Minuten</td>
    <td class="stats_data">$current.rain</td>
   </tr>
   <tr>
    <td class="stats_label">Niederschlag heute<br />seit Mitternacht</td>
    <td class="stats_data">$day.rain.sum</td>
  </tr>
  <tr>
    <td class="stats_label">Regenintensität,<br />der letzten 5 Minuten</td>
    <td class="stats_data">$current.rainRate</td>
  </tr>
  <tr>
    <td class="stats_label">Regenintensität<br />&nbsp;</td>
    <td class="stats_data">$day.rainRate.max</td>
  </tr>
  <tr>
    <td class="stats_label">Letzter Niederschlag<br />&nbsp;</td>
    <td class="stats_data">$lastrain_day <br /> $lastrain_delta_time</td>
  </tr>
  <tr><td>1-Wire  OWFS USB</td><td>&nbsp;</td></tr>
  #if $day.extraTemp4.has_data
  <tr>
   <td class="stats_label">Garten<br />&nbsp;</td>
   <td class="stats_data">$current.extraTemp4</td>
  </tr>
  #end if
  #if $day.extraTemp8.has_data
  <tr>
   <td class="stats_label">Schwimmsteg<br />ca. 1,80 m&nbsp;</td>
   <td class="stats_data">$current.extraTemp8</td>
  </tr>
  #end if
  <tr><td>Wassertemperatur</td><td>Info</td></tr>
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
  <tr><td>Sonne</td><td>Info</td></tr>
  #if $day.lighting.has_data
  <tr>
   <td class="stats_label">Beleuchtungsstärke<br />(Illuminance)</td>
   <td class="stats_data">$current.lighting</td>
  </tr>
  #end if
  #if $day.UV.has_data
  <tr>
    <td class="stats_label">UV<br />&nbsp;</td>
   #if $current.UV.raw <= 2.4
    <td class="stats_data" style="background-color: limegreen">$current.UV</td>
   #else if $current.UV.raw >= 2.5 and $current.UV.raw <= 5.4
    <td class="stats_data" style="background-color: yellow">$current.UV</td>
   #else if $current.UV.raw >= 5.5 and $current.UV.raw <= 7.4
    <td class="stats_data" style="background-color: orange">$current.UV</td>
   #else if $current.UV.raw >= 7.5 and $current.UV.raw <= 10.4
    <td class="stats_data" style="background-color: red">$current.UV</td>
   #else if $current.UV.raw > 10.5
    <td class="stats_data" style="background-color: violet">$current.UV</td>
   #end if
   </tr>
  #end if
  #if $day.ET.has_data and $day.ET.sum.raw > 0.0
   <tr>
    <td class="stats_label">ET<br />Berechnung in weewx&nbsp;</td>
    <td class="stats_data">$current.ET</td>
   </tr>
  #end if
  #if $day.radiation.has_data
   <tr>
    <td class="stats_label">Globalstrahlung<br />&nbsp;</td>
    <td class="stats_data">$current.radiation</td>
   </tr>
  #end if
  #if $day.sunshinehours.has_data
   <tr>
    <td class="stats_label">Sonnestunden<br />Aktuell</td>
    <td class="stats_data">$current.sunshinehours.format("%.2f")&nbsp;h</td>
   </tr>
   <tr>
    <td class="stats_label">Sonnestunden am Tag<br />Berechnung&nbsp;</td>
    <td class="stats_data">$day.sunshineS.sum.hour</td>
   </tr>
  #end if
   <tr><td>Bodentemperatur</td><td>Info</td></tr>
  #if $day.extraTemp7.has_data
   <tr>
    <td class="stats_label">Boden +100cm<br />&nbsp;</td>
    <td class="stats_data">$current.extraTemp7</td>
   </tr>
  #end if
  #if $day.extraTemp5.has_data
   <tr>
    <td class="stats_label">Boden +5cm<br />&nbsp;</td>
    <td class="stats_data">$current.extraTemp5</td>
   </tr>
  #end if
  #if $day.soilTemp1.has_data
   <tr>
    <td class="stats_label">Boden -5cm<br />&nbsp;</td>
    <td class="stats_data">$current.soilTemp1</td>
   </tr>
  #end if
  #if $day.soilTemp2.has_data
   <tr>
    <td class="stats_label">Boden -10cm<br />&nbsp;</td>
    <td class="stats_data">$current.soilTemp2</td>
   </tr>
  #end if
  #if $day.soilTemp3.has_data
   <tr>
    <td class="stats_label">Boden -20cm<br />&nbsp;</td>
    <td class="stats_data">$current.soilTemp3</td>
   </tr>
  #end if
  #if $day.soilTemp4.has_data
   <tr>
    <td class="stats_label">Boden -50cm<br />&nbsp;</td>
    <td class="stats_data">$current.soilTemp4</td>
   </tr>
  #end if
  #if $day.soilTemp5.has_data
   <tr>
    <td class="stats_label">Boden -100cm<br />&nbsp;</td>
    <td class="stats_data">$current.soilTemp5</td>
   </tr>
  #end if
   <tr><td>Bodenfeuchtigkeit</td><td>Info</td></tr>
  #if $day.soilMoist1.has_data
   <tr>
    <td class="stats_label">Bodenfeuchte bei<br />-5 cm</td>
    <td class="stats_data">$current.soilMoist1</td>
   </tr>
  #end if
  #if $day.soilMoist2.has_data
   <tr>
    <td class="stats_label">Bodenfeuchte<br />-10 cm&nbsp;</td>
    <td class="stats_data">$current.soilMoist2</td>
   </tr>
  #end if
  #if $day.soilMoist3.has_data
   <tr>
    <td class="stats_label">Bodenfeuchte<br />-20 cm&nbsp;</td>
    <td class="stats_data">$current.soilMoist3</td>
   </tr>
  #end if
  #if $day.soilMoist4.has_data
   <tr>
    <td class="stats_label">Bodenfeuchte<br />-50 cm&nbsp;</td>
    <td class="stats_data">$current.soilMoist4</td>
   </tr>
  #end if
   <tr>
    <td>Büro</td><td>Info</td>
   </tr>
   <tr>
    <td class="stats_label">Temperatur (innen)<br />&nbsp;</td>
    <td class="stats_data">$current.inTemp</td>
   </tr>
   <tr>
     <td class="stats_label">Luftfeuchte (innen)<br />&nbsp;</td>
     <td class="stats_data">$current.inHumidity</td>
   </tr>
   <tr>
     <td class="stats_label">Taupunkt (innen)<br />&nbsp;</td>
     <td class="stats_data">$current.inDewpoint</td>
   </tr>
   <tr>
     <td class="stats_label">Masszahl für den Wärmebedarfs<br /> eine Gebäudes. Basis 18 °C.</td>
     <td class="stats_data">$day.heatdeg.sum</td>
   </tr>
   <tr>
     <td class="stats_label">Masszahl zur Kühlung <br />eines Gebäudes. Basis 18 °C</td>
     <td class="stats_data">$day.cooldeg.sum</td>
   </tr>
   <tr>
    <td class="stats_label">Kühlgrenztemperatur<br />Feuchte Kugel Temperatur</td>
    <td class="stats_data">$WB</td>
   </tr>
  </tbody>
 </table>
</div>
<p>&nbsp;</p><!-- End current -->


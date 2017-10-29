#encoding UTF-8
## cwerte.inc
        <div class="stats">
          <div class="stats_header">
            $wertename
          </div>

          <table>
            <tbody>
              <tr>
                <td class="stats_label">
                  Temperatur (max)<br />
                  Temperatur (min)
                </td>
                <td class="stats_data">
                  $werte.outTemp.max&nbsp;$wertum&nbsp; $werte.outTemp.maxtime<br />
                  $werte.outTemp.min&nbsp;$wertum&nbsp; $werte.outTemp.mintime
                </td>
              </tr>
              <tr>
                <td class="stats_label">
                  scheinbare (max)<br />
                  Temperatur (min)
                </td>
                <td class="stats_data">
                  $werte.appTemp.max&nbsp;$wertum&nbsp; $werte.appTemp.maxtime<br />
                  $werte.appTemp.min&nbsp;$wertum&nbsp; $werte.appTemp.mintime
                </td>
              </tr>
              <tr>
                <td class="stats_label">
                  Hitzeindex (max)<br />&nbsp;
                </td>
                <td class="stats_data"> 
                  $werte.heatindex.max&nbsp;$wertum&nbsp; $werte.heatindex.maxtime
                </td>
              </tr>
              <tr>
                <td class="stats_label"> 
                  Windchill (min)<br />&nbsp;
                </td>
                <td class="stats_data"> 
                  $werte.windchill.min&nbsp;$wertum&nbsp; $werte.windchill.mintime
                </td>
              </tr>
              <tr>
                <td class="stats_label">
                  Taupunkt (max)<br />
                  Taupunkt (min)
                </td>
                <td class="stats_data">
                  $werte.dewpoint.max&nbsp;$wertum&nbsp; $werte.dewpoint.maxtime<br />
                  $werte.dewpoint.min&nbsp;$wertum&nbsp; $werte.dewpoint.mintime
                </td>
              </tr>
              <tr>
                <td class="stats_label">
                  Luftfeuchte (max)<br />
                  Luftfeuchte (min)
                </td>
                <td class="stats_data">
                  $werte.outHumidity.max&nbsp;$wertum&nbsp; $werte.outHumidity.maxtime<br />
                  $werte.outHumidity.min&nbsp;$wertum&nbsp; $werte.outHumidity.mintime
                </td>
              </tr>
              <tr>
                <td class="stats_label">
                  Luftfeuchte absolut(max)<br />
                  Luftfeuchte        (min)
                </td>
                <td class="stats_data">
                  $werte.absolutF.max&nbsp;$wertum&nbsp; $werte.absolutF.maxtime<br />
                  $werte.absolutF.min&nbsp;$wertum&nbsp; $werte.absolutF.mintime
                </td>
              </tr>
              <tr>
                <td class="stats_label">
                  Hum-Index (max)<br />
                  Hum-Index (min)
                </td>
                <td class="stats_data">
                  $werte.humidex.max&nbsp;$wertum&nbsp; $werte.humidex.maxtime<br />
                  $werte.humidex.min&nbsp;$wertum&nbsp; $werte.humidex.mintime
                </td>
              </tr>
              <tr>
                <td class="stats_label">
                  Luftdruck (max)<br />
                  Luftdruck (min)
                </td>
                <td class="stats_data">
                  $werte.barometer.max&nbsp;$wertum&nbsp; $werte.barometer.maxtime<br />
                  $werte.barometer.min&nbsp;$wertum&nbsp; $werte.barometer.mintime
                </td>
              </tr>
              <tr>
                <td class="stats_label">
                  Luftdichte (max)<br />
                  Luftdichte (min)
                </td>
                <td class="stats_data">
                  $werte.airDensity.max&nbsp;$wertum&nbsp; $werte.airDensity.maxtime<br />
                  $werte.airDensity.min&nbsp;$wertum&nbsp; $werte.airDensity.mintime
                </td>
              </tr>
              <tr>
                <td class="stats_label">
                  Regen Total<br />&nbsp;
                </td>
                <td class="stats_data">
                  $werte.rain.sum
                </td>
              </tr>
              <tr>
                <td class="stats_label"> 
                  Regenintensität (max)<br />&nbsp;
                </td>
                <td class="stats_data">
                  $werte.rainRate.max&nbsp;$wertum&nbsp; $werte.rainRate.maxtime
                </td>
              </tr>
              <tr>
                <td class="stats_label">
                  Schneehöhe<br />&nbsp;
                </td>
                <td class="stats_data">
                  $werte.snow.max&nbsp;$wertum&nbsp; $werte.snow.maxtime
                </td>
              </tr>
              <tr>
                <td class="stats_label">
                  Verdunstung (max)<br />&nbsp;
                </td>
                <td class="stats_data">
                  $werte.ET.max
                </td>
              </tr>
              <tr>
                <td class="stats_label">
                  Windgeschwindigkeit (max)<br />&nbsp;
                </td>
                <td class="stats_data">
                  $werte.wind.max aus $werte.wind.gustdir&nbsp;$wertum&nbsp; $werte.wind.maxtime
                </td>
              </tr>
              <tr>
                <td class="stats_label">
                  Windgeschwindigkeit &Oslash;<br />&nbsp;
                </td>
                <td class="stats_data">
                  $werte.wind.avg
                </td>
              </tr>
              <tr>
                <td class="stats_label">
                  RMS Wind<br />&nbsp;
                </td>
                <td class="stats_data">
                  $werte.wind.rms
                </td>
              </tr>
              <tr>
                <td class="stats_label">
                  &Oslash; Geschwindigkeit<br />
                  &Oslash; Himmelsrichtung 
                </td>
                <td class="stats_data">
                  $werte.wind.vecavg<br />
                  $werte.wind.vecdir
                </td>
              </tr>
              <tr><td>1-Wire Sensoren USB</td><td></tr>
            #if $werte.extraTemp1.has_data
              <tr>
                <td class="stats_label">
                  Teich Temperatur (max)<br />
                  Teich Temperatur (min)
                </td>
                <td class="stats_data">
                  $werte.extraTemp1.max&nbsp;$wertum&nbsp; $werte.extraTemp1.maxtime<br />
                  $werte.extraTemp1.min&nbsp;$wertum&nbsp; $werte.extraTemp1.mintime
                </td>
              </tr>
            #end if
            #if $werte.extraTemp2.has_data
              <tr>
                <td class="stats_label">
                  Schwimmteich Temperatur (max)<br />
                  Schwimmteich Temperatur (min)
                </td>
                <td class="stats_data">
                  $werte.extraTemp2.max&nbsp;$wertum&nbsp; $werte.extraTemp2.maxtime<br />
                  $werte.extraTemp2.min&nbsp;$wertum&nbsp; $werte.extraTemp2.mintime
                </td>
              </tr>
            #end if
            #if $werte.extraTemp3.has_data
              <tr>
                <td class="stats_label">
                  Schwimmteich -1,8m Temperatur (max)<br />
                  Schwimmteich -1,8m Temperatur (min)
                </td>
                <td class="stats_data">
                  $werte.extraTemp3.max&nbsp;$wertum&nbsp; $werte.extraTemp3.maxtime<br />
                  $werte.extraTemp3.min&nbsp;$wertum&nbsp; $werte.extraTemp3.mintime
                </td>
              </tr>
            #end if
            #if $werte.extraTemp6.has_data
              <tr>
                <td class="stats_label">
                  Gartenteich Temperatur (max)<br />
                  Gartenteich Temperatur (min)
                </td>
                <td class="stats_data">
                  $werte.extraTemp6.max&nbsp;$wertum&nbsp; $werte.extraTemp6.maxtime<br />
                  $werte.extraTemp6.min&nbsp;$wertum&nbsp; $werte.extraTemp6.mintime
                </td>
              </tr>
            #end if
            #if $werte.extraTemp8.has_data
              <tr>
                <td class="stats_label">
                  Schwimmsteg Temperatur (max)<br />
                  Schwimmsteg Temperatur (min)
                </td>
                <td class="stats_data">
                  $werte.extraTemp8.max&nbsp;$wertum&nbsp; $werte.extraTemp8.maxtime<br />
                  $werte.extraTemp8.min&nbsp;$wertum&nbsp; $werte.extraTemp8.mintime
                </td>
              </tr>
            #end if
            #if $werte.extraTemp4.has_data
              <tr>
                <td class="stats_label">
                  Garten/ Carport Temperatur (max)<br />
                  Garten/ Carport Temperatur (min)
                </td>
                <td class="stats_data">
                  $werte.extraTemp4.max&nbsp;$wertum&nbsp; $werte.extraTemp4.maxtime<br />
                  $werte.extraTemp4.min&nbsp;$wertum&nbsp; $werte.extraTemp4.mintime
                </td>
              </tr>
            #end if
            #if $werte.extraTemp7.has_data
              <tr>
                <td class="stats_label">
                  Temperatur + 100cm (max)<br />
                  Temperatur + 100cm (min)
                </td>
                <td class="stats_data">
                  $werte.extraTemp7.max&nbsp;$wertum&nbsp; $werte.extraTemp7.maxtime<br />
                  $werte.extraTemp7.min&nbsp;$wertum&nbsp; $werte.extraTemp7.mintime
                </td>
              </tr>
            #end if
            <tr><td>Sonne</td><td>&nbsp;</td></tr>
            #if $werte.lighting.has_data
              <tr>
                <td class="stats_label">
                  Helligkeit (max)<br />
                  &nbsp; 
                </td>
                <td class="stats_data">
                  $werte.lighting.max&nbsp;$wertum&nbsp; $werte.lighting.maxtime
                </td>
              </tr>
            #end if

            #if $werte.UV.has_data
              <tr>
                <td class="stats_label">
                  UV-Index (max)<br />&nbsp;
               </td>
                <td class="stats_data">
                  $werte.UV.max&nbsp;$wertum&nbsp; $werte.UV.maxtime<br />
                </td>
              </tr>
             #end if

             #if $werte.radiation.has_data
              <tr>
                <td class="stats_label">
                  Sonnenstrahlung (max)<br />&nbsp;
                </td>
                <td class="stats_data">
                  $werte.radiation.max&nbsp;$wertum&nbsp; $werte.radiation.maxtime<br />
                </td>
              </tr>
              <tr>
                <td class="stats_label">
                  Sonnenstrahlung (Summe)<br />&nbsp;
                </td>
                <td class="stats_data">
                  $werte.radiation.sum<br />
                </td>
              </tr>
             #end if
             #if $werte.sunshineS.has_data 
              <tr>
                <td class="stats_label">
                  Sonnenscheindauer berechnet (max)<br />
                 &nbsp;
                </td>
                <td class="stats_data">
                  $werte.sunshineS.sum.format("%.2f")
                </td>
              </tr>
             #end if
            <tr><td>Boden</td><td>&nbsp;</td></tr>
            #if $werte.extraTemp5.has_data
              <tr>
                <td class="stats_label">
                  BodenTemp 5 cm (max)<br />
                  BodenTemp 5 cm (min)
                </td>
                <td class="stats_data">
                  $werte.extraTemp5.max&nbsp;$wertum&nbsp; $werte.extraTemp5.maxtime<br />
                  $werte.extraTemp5.min&nbsp;$wertum&nbsp; $werte.extraTemp5.mintime
                </td>
              </tr>
            #end if

            #if $werte.soilTempO1.has_data
              <tr>
                <td class="stats_label">
                  BodenTemp -5 cm (max)<br />
                  BodenTemp -5 cm (min)
                </td>
                <td class="stats_data">
                  $werte.soilTempO1.max&nbsp;$wertum&nbsp; $werte.soilTempO1.maxtime<br />
                  $werte.soilTempO1.min&nbsp;$wertum&nbsp; $werte.soilTempO1.mintime
                </td>
              </tr>
            #end if
            #if $werte.soilTempO2.has_data
              <tr>
                <td class="stats_label">
                  BodenTemp -10 cm (max)<br />
                  BodenTemp -10 cm (min)
                </td>
                <td class="stats_data">
                  $werte.soilTempO2.max&nbsp;$wertum&nbsp; $werte.soilTempO2.maxtime<br />
                  $werte.soilTempO2.min&nbsp;$wertum&nbsp; $werte.soilTempO2.mintime
                </td>
              </tr>
              #end if
              #if $werte.soilTempO3.has_data
              <tr>
                <td class="stats_label">
                  BodenTemp -20 cm (max)<br />
                  BodenTemp -20 cm (min)
                </td>
                <td class="stats_data">
                  $werte.soilTempO3.max&nbsp;$wertum&nbsp; $werte.soilTempO3.maxtime<br />
                  $werte.soilTempO3.min&nbsp;$wertum&nbsp; $werte.soilTempO3.mintime
                </td>
              </tr>
              #end if
              #if $werte.soilTempO4.has_data
              <tr>
                <td class="stats_label">
                  BodenTemp -50 cm (max)<br />
                  BodenTemp -50 cm (min)
                </td>
                <td class="stats_data">
                  $werte.soilTempO4.max&nbsp;$wertum&nbsp; $werte.soilTempO4.maxtime<br />
                  $werte.soilTempO4.min&nbsp;$wertum&nbsp; $werte.soilTempO4.mintime
                </td>
              </tr>
              #end if
              #if $werte.soilTempO5.has_data
              <tr>
                <td class="stats_label">
                  BodenTemp -100 cm (max)<br />
                  BodenTemp -100 cm (min)
                </td>
                <td class="stats_data">
                  $werte.soilTempO5.max&nbsp;$wertum&nbsp; $werte.soilTempO5.maxtime<br />
                  $werte.soilTempO5.min&nbsp;$wertum&nbsp; $werte.soilTempO5.mintime
                </td>
              </tr>
              #end if
             <tr><td>Büro</td><td>&nbsp;</td></tr>
              <tr>
                <td class="stats_label">
                  Temperatur (innen max)<br />
                  Temperatur (innen min)
                </td>
                <td class="stats_data">
                  $werte.inTemp.max&nbsp;$wertum&nbsp; $werte.inTemp.maxtime<br />
                  $werte.inTemp.min&nbsp;$wertum&nbsp; $werte.inTemp.mintime
                </td>
              </tr>
              <tr>
                <td class="stats_label">
                  Luftfeuchte (innen max)<br />
                  Luftfeuchte (innen min)
                </td>
                <td class="stats_data">
                  $werte.inHumidity.max&nbsp;$wertum&nbsp; $werte.inHumidity.maxtime<br />
                  $werte.inHumidity.min&nbsp;$wertum&nbsp; $werte.inHumidity.mintime
                </td>
              </tr>
              <tr>
                <td class="stats_label">
                  Taupunkt (innen max)<br />
                  Taupunkt (innen min)
                </td>
                <td class="stats_data">
                  $werte.inDewpoint.max&nbsp;$wertum&nbsp; $werte.inDewpoint.maxtime<br />
                  $werte.inDewpoint.min&nbsp;$wertum&nbsp; $werte.inDewpoint.mintime
                </td>
              </tr>
            </tbody>
          </table>
        </div> <!-- End class "stats" -->


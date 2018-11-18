#encoding UTF-8
## summeNeu.inc 2749 2015-01-06 18:15:24Z hes $

 <table>
  <tr><td>Anzahl der Tage mit </td><td>2015</td><td>2014</td><td>2013</td></tr>
  <tr>
   <td style="background-color: #FF6969">Höchsttemperatur >= 30°C (heißer Tag)      </td>
   <td style="background-color: #FF6969">$year.outTemp.max_ge((30.0, "degree_C", "group_temperature")).format("%.0f")</td>
   <td style="background-color: #FF6969">$year1.outTemp.max_ge((30.0, "degree_C", "group_temperature")).format("%.0f")</td>
   <td style="background-color: #FF6969">$year2.outTemp.max_ge((30.0, "degree_C", "group_temperature")).format("%.0f")</td>
  </tr>
  <tr><td style="background-color: #FFAC4B">Höchsttemperatur >= 25°C (Sommertag)       </td>
   <td style="background-color: #FFAC4B">$year.outTemp.max_ge((25.0, "degree_C", "group_temperature")).format("%.0f")</td>
   <td style="background-color: #FFAC4B">$year1.outTemp.max_ge((25.0, "degree_C", "group_temperature")).format("%.0f")</td>
   <td style="background-color: #FFAC4B">$year2.outTemp.max_ge((25.0, "degree_C", "group_temperature")).format("%.0f")</td>
  </tr>
  <tr>
   <td style="background-color: #FF8C5F">Tiefsttemperatur >= 20°C (tropische Nacht) </td>
   <td style="background-color: #FF8C5F">$year.outTemp.min_ge((20.0, "degree_C", "group_temperature")).format("%.0f")</td>
   <td style="background-color: #FF8C5F">$year1.outTemp.min_ge((20.0, "degree_C", "group_temperature")).format("%.0f")</td>
   <td style="background-color: #FF8C5F">$year2.outTemp.min_ge((20.0, "degree_C", "group_temperature")).format("%.0f")</td>
  </tr>
  <tr>
   <td style="background-color: #FFAC4B">Höchsttemperatur >= 20°C (warmer Tag)       </td>
   <td style="background-color: #FFAC4B">$year.outTemp.max_ge((20.0, "degree_C", "group_temperature")).format("%.0f")</td>
   <td style="background-color: #FFAC4B">$year1.outTemp.max_ge((20.0, "degree_C", "group_temperature")).format("%.0f")</td>
   <td style="background-color: #FFAC4B">$year2.outTemp.max_ge((20.0, "degree_C", "group_temperature")).format("%.0f")</td>
  </tr>
  <tr>
   <td style="background-color: #ECFF4B">Temperatur < 15°C  (Heiztag)      </td>
   <td style="background-color: #ECFF4B">$year.outTemp.max_le((15.0, "degree_C", "group_temperature")).format("%.0f")</td>
   <td style="background-color: #ECFF4B">$year1.outTemp.max_le((15.0, "degree_C", "group_temperature")).format("%.0f")</td>
   <td style="background-color: #ECFF4B">$year2.outTemp.max_le((15.0, "degree_C", "group_temperature")).format("%.0f")</td>
  </tr>
  <tr>
   <td style="background-color: #ECFF4B">Höchsttemperatur < 10°C  (kalter Tag)      </td>
   <td style="background-color: #ECFF4B">$year.outTemp.max_le((10.0, "degree_C", "group_temperature")).format("%.0f")</td>
   <td style="background-color: #ECFF4B">$year1.outTemp.max_le((10.0, "degree_C", "group_temperature")).format("%.0f")</td>
   <td style="background-color: #ECFF4B">$year2.outTemp.max_le((10.0, "degree_C", "group_temperature")).format("%.0f")</td>
  </tr>
  <tr>
   <td style="background-color: #33FF33">Tiefsttemperatur >= 5°C  (Vegetationstag)  </td>
   <td style="background-color: #33FF33">$year.outTemp.min_ge((5.0, "degree_C", "group_temperature")).format("%.0f")</td>
   <td style="background-color: #33FF33">$year1.outTemp.min_ge((5.0, "degree_C", "group_temperature")).format("%.0f")</td>
   <td style="background-color: #33FF33">$year2.outTemp.min_ge((5.0, "degree_C", "group_temperature")).format("%.0f")</td>
  </tr>
  <tr>
   <td style="background-color: #23FF9E">Höchsttemperatur < 0°C  (Eistag)        </td>
   <td style="background-color: #23FF9E">$year.outTemp.max_le((0.0, "degree_C", "group_temperature")).format("%.0f")</td>
   <td style="background-color: #23FF9E">$year1.outTemp.max_le((0.0, "degree_C", "group_temperature")).format("%.0f")</td>
   <td style="background-color: #23FF9E">$year2.outTemp.max_le((0.0, "degree_C", "group_temperature")).format("%.0f")</td>
  </tr>
  <tr>
   <td style="background-color: #4B84FF">Tiefsttemperatur < 0°C (Frosttag)          </td>
   <td style="background-color: #4B84FF">$year.outTemp.min_le((0.0, "degree_C", "group_temperature")).format("%.0f")</td>
   <td style="background-color: #4B84FF">$year1.outTemp.min_le((0.0, "degree_C", "group_temperature")).format("%.0f")</td>
   <td style="background-color: #4B84FF">$year2.outTemp.min_le((0.0, "degree_C", "group_temperature")).format("%.0f")</td>
  </tr>
  <tr>
   <td style="background-color: #4B84FF">Tiefsttemperatur < -10°C (sehr Kalter Tag) </td>
   <td style="background-color: #4B84FF">$year.outTemp.min_le((-10.0, "degree_C", "group_temperature")).format("%.0f")</td>
   <td style="background-color: #4B84FF">$year1.outTemp.min_le((-10.0, "degree_C", "group_temperature")).format("%.0f")</td>
   <td style="background-color: #4B84FF">$year2.outTemp.min_le((-10.0, "degree_C", "group_temperature")).format("%.0f")</td>
  </tr>
 </table>

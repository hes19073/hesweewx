#encoding UTF-8
##  summe.inc 2749 2015-01-06 18:15:24Z hes $

<table>
 <tr>
  <td>Anzahl der <br />nach Jahren</td>
  <td style="background-color: #FF4949">Wüstentag      <br />T<sub>max</sub> >= 35°C</td>
  <td style="background-color: #FF6969">Heißer Tag     <br />T<sub>max</sub> >= 30°C</td>
  <td style="background-color: #FF8C5F">Tropennacht    <br />T<sub>min</sub> >= 20°C</td>
  <td style="background-color: #FFAC4B">Sommertag      <br />T<sub>max</sub>>= 25°C</td>
  <td style="background-color: #33FF33">Vegetationstag <br />T<sub>min</sub> >= 5°C</td>
  <td style="background-color: #23FF9E">Frosttag       <br />T<sub>min</sub> < 0°C</td>
  <td style="background-color: #4B84FF">Eistag         <br />T<sub>max</sub> < 0 °C</td>
  <td style="background-color: #4B84FF">Kalter Tag     <br />T<sub>min</sub> < -10 °C</td>
  <td style="background-color: #4B84FF">Sehr kalter Tag<br />T<sub>min</sub>< -15 °C</td>
 </tr>
#for $year in $alltime.years
 <tr>
  <td>$year.dateTime.format("%Y")</td>
  <td style="background-color: #FF4949">$year.outTemp.max_ge((35.0, "degree_C", "group_temperature")).format("%.0f")</td>
  <td style="background-color: #FF6969">$year.outTemp.max_ge((30.0, "degree_C", "group_temperature")).format("%.0f")</td>
  <td style="background-color: #FF8C5F">$year.outTemp.min_ge((20.0, "degree_C", "group_temperature")).format("%.0f")</td>
  <td style="background-color: #FFAC4B">$year.outTemp.max_ge((25.0, "degree_C", "group_temperature")).format("%.0f")</td>
  <td style="background-color: #33FF33">$year.outTemp.max_ge((5.0, "degree_C", "group_temperature")).format("%.0f")</td>
  <td style="background-color: #23FF9E">$year.outTemp.min_le((0.0, "degree_C", "group_temperature")).format("%.0f")</td>
  <td style="background-color: #4B84FF">$year.outTemp.max_le((0.0, "degree_C", "group_temperature")).format("%.0f")</td>
  <td style="background-color: #4B84FF">$year.outTemp.min_le((-10.0, "degree_C", "group_temperature")).format("%.0f")</td>
  <td style="background-color: #4B84FF">$year.outTemp.min_le((-15.0, "degree_C", "group_temperature")).format("%.0f")</td>
 </tr>
#end for
</table>
<hr />

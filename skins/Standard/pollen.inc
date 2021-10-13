#encoding UTF-8
##  pollen.inc 2749 2019-01-19 14:15:24Z hes $
#import datetime
<div class="hes">
 <div class='hesbox'>
 <table>
  <tr><td class='hes1_kopfa' colspan='3'>
   <a href='https://www.dwd.de/DE/leistungen/gefahrenindizespollen/gefahrenindexpollen.html' target='_blank'>Pollenvorhersage</a></td></tr>
  <tr><td colspan='3'> -Medizin-Meteorologie-</td></tr>
  #set $ts = datetime.datetime.fromtimestamp($las_up).strftime('%d.%m.%Y %H:%M')
  <tr><td colspan='3'> erstellt: $ts  Uhr UTC<br />
   für: $region</td></tr>
  <tr><td><b>Pollenart</b></td><td><b>Heute</b></td><td><b>Morgen</b></td></tr>
  <tr><td>Hasel</td>
     <td>$hasel_h</td>
     <td>$hasel_m</td></tr>
  <tr><td>Erle </td>
     <td>$erle_h</td>
     <td>$erle_m</td></tr>
  <tr><td>Esche</td>
     <td>$esche_h</td>
     <td>$esche_m</td></tr>
  <tr><td>Birke</td>
     <td>$birke_h</td>
     <td>$birke_m</td></tr>
  <tr><td>Gräser</td>
     <td>$graeser_h</td>
     <td>$graeser_m</td></tr>
  <tr><td>Roggen</td>
     <td>$roggen_h</td>
     <td>$roggen_m</td></tr>
  <tr><td>Beifuss</td>
     <td>$beifuss_h</td>
     <td>$beifuss_m</td></tr>
  <tr><td>Ambrosia</td>
     <td>$ambrosia_h</td>
     <td>$ambrosia_m</td></tr>
 </table><hr />
   <ul>
     <li><b>&nbsp; 0 &nbsp;</b>  keine &nbsp;
         <b>0-1</b>  bis geringe Belastung</li>
     <li><b>&nbsp; 1 &nbsp;</b>  geringe &nbsp;
         <b>1-2</b>  bis mittlere Belastung</li>
     <li><b>&nbsp; 2 &nbsp;</b>  mittlere &nbsp;
         <b>2-3</b>  bis hohe Belastung</li>
     <li><b> 3 </b>  hohe Belastung &nbsp;&nbsp;|&nbsp;&nbsp; 
         <a href='https://opendata.dwd.de/climate_environment/health/alerts/s31fg.json' target='_blank'> Quelle:DWD </a></li>
  </ul>
 </div>
</div> <!-- end pollen -->


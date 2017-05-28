#encoding UTF-8
#if $latest($data_binding='dwd_binding')hasel_n.has_data
<table>
 <thead><tr><th>Pollenart</th><th>Heute</th><th>Morgen</th><th>Übermorgen</th></tr></thead>
 <tr><td>Hasel</td>
     <td>$latest($data_binding='dwd_binding')hasel_h.raw</td>
     <td>$latest($data_binding='dwd_binding')hasel_m.raw</td>
     <td>$latest($data_binding='dwd_binding')hasel_n.raw</td></tr>
 <tr><td>Erle </td>
     <td>$latest($data_binding='dwd_binding')erle_h.raw</td>
     <td>$latest($data_binding='dwd_binding')erle_m.raw</td>
     <td>$latest($data_binding='dwd_binding')erle_n.raw</td></tr>
 <tr><td>Esche</td>
     <td>$latest($data_binding='dwd_binding')esche_h.raw</td>
     <td>$latest($data_binding='dwd_binding')esche_m.raw</td>
     <td>$latest($data_binding='dwd_binding')esche_n.raw</td></tr>
 <tr><td>Birke</td>
     <td>$latest($data_binding='dwd_binding')birke_h.raw</td>
     <td>$latest($data_binding='dwd_binding')birke_m.raw</td>
     <td>$latest($data_binding='dwd_binding')birke_n.raw</td></tr>
 <tr><td>Gräser</td>
     <td>$latest($data_binding='dwd_binding')graeser_h.raw</td>
     <td>$latest($data_binding='dwd_binding')graeser_m.raw</td>
     <td>$latest($data_binding='dwd_binding')graeser_m.raw</td></tr>
 <tr><td>Roggen</td>
     <td>$latest($data_binding='dwd_binding')roggen_h.raw</td>
     <td>$latest($data_binding='dwd_binding')roggen_m.raw</td>
     <td>$latest($data_binding='dwd_binding')roggen_n.raw</td></tr>
 <tr><td>Beifuss</td>
     <td>$latest($data_binding='dwd_binding')beifuss_h.raw</td>
     <td>$latest($data_binding='dwd_binding')beifuss_m.raw</td>
     <td>$latest($data_binding='dwd_binding')beifuss_n.raw</td></tr>
 <tr><td>Ambrosia</td>
     <td>$latest($data_binding='dwd_binding')ambrosia_h.raw</td>
     <td>$latest($data_binding='dwd_binding')ambrosia_m.raw</td>
     <td>$latest($data_binding='dwd_binding')ambrosia_n.raw</td></tr>
</table>
#else 
    <table>
 <thead><tr><th>Pollenart</th><th>Heute</th><th>Morgen</th></tr></thead>
 <tr><td>Hasel</td>
     <td>$latest($data_binding='dwd_binding')hasel_h.raw</td>
     <td>$latest($data_binding='dwd_binding')hasel_m.raw</td></tr>
 <tr><td>Erle </td>
     <td>$latest($data_binding='dwd_binding')erle_h.raw</td>
     <td>$latest($data_binding='dwd_binding')erle_m.raw</td></tr>
 <tr><td>Esche</td>
     <td>$latest($data_binding='dwd_binding')esche_h.raw</td>
     <td>$latest($data_binding='dwd_binding')esche_m.raw</td></tr>
 <tr><td>Birke</td>
     <td>$latest($data_binding='dwd_binding')birke_h.raw</td>
     <td>$latest($data_binding='dwd_binding')birke_m.raw</td></tr>
 <tr><td>Gräser</td>
     <td>$latest($data_binding='dwd_binding')graeser_h.raw</td>
     <td>$latest($data_binding='dwd_binding')graeser_m.raw</td></tr>
 <tr><td>Roggen</td>
     <td>$latest($data_binding='dwd_binding')roggen_h.raw</td>
     <td>$latest($data_binding='dwd_binding')roggen_m.raw</td></tr>
 <tr><td>Beifuss</td>
     <td>$latest($data_binding='dwd_binding')beifuss_h.raw</td>
     <td>$latest($data_binding='dwd_binding')beifuss_m.raw</td></tr>
 <tr><td>Ambrosia</td>
     <td>$latest($data_binding='dwd_binding')ambrosia_h.raw</td>
     <td>$latest($data_binding='dwd_binding')ambrosia_m.raw</td></tr>
 </table>
#end if
<hr />
 <table>
 <tr><td colspan="3">Deutscher Wetterdienst - Medizin-Meteorologie</td></tr>
 <tr><td colspan="3">Legende</td></tr>
 <tr><td>0</td><td colspan="2"> keine Belastung</td></tr>
 <tr><td>0-1</td><td colspan="2">  keine bis geringe Belastung</td></tr>
 <tr><td>1</td><td colspan="2">  geringe Belastung</td></tr>
 <tr><td>1-2</td><td colspan="2">  geringe bis mittlere Belastung</td></tr>
 <tr><td>2</td><td colspan="2">  mittlere Belastung</td></tr>
 <tr><td>2-3</td><td colspan="2">  mittlere bis hohe Belastung</td></tr>
 <tr><td>3</td><td colspan="2">  hohe Belastung</td></tr>
 <tr><td colspan="3">Quelle: DWD</td></tr>
</table>

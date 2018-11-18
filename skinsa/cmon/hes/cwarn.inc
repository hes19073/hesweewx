#encoding UTF-8
## cwarn.inc 2015-02-23 18:24:18Z hes $

<p>&nbsp;</p>

#if $latest($data_binding='weewx_binding').outTemp.raw > 26.7
 <div id="fzei">
 #if $latest($data_binding='weewx_binding').heatindex.raw > 26.7 and $latest($data_binding='weewx_binding').heatindex.raw < 33
  <p style="background-color: gold"><strong>Vorsicht!!!</strong><br />Erschöpfung möglich bei längerer Aktivität.</p>
 #elif $latest($data_binding='weewx_binding').heatindex.raw > 32 and $latest($data_binding='weewx_binding').heatindex.raw < 42
  <p style="background-color: lightpink"><strong>Erhöhte Vorsicht!!!</strong><br /> Möglichkeit von Hitzeschäden wie Sonnenstich, Hitzekrampf und Hitzekollaps.</p>
 #elif $latest($data_binding='weewx_binding').heatindex.raw > 41 and $latest($data_binding='weewx_binding').hestindex.rwa < 55
  <p style="background-color: lightsalmon"><strong>Gefahr!!!</strong><br />Sonnenstich, Hitzekrampf und Hitzekollaps sind wahrscheinlich; Hitzeschlag ist möglich.</p>
 #elif $latest($data_binding='weewx_binding').heatindex.raw > 54
  <p style="background-color: hotpink"><strong>Erhöhte Gefahr!!!</strong><br />Hitzschlag und Sonnenstich sind wahrscheinlich bei längerem Aufenthalt</p>
 #end if
 </div>
#end if


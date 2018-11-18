#encoding UTF-8
## cwarn.inc 2015-02-23 18:24:18Z hes $

<p>&nbsp;</p>

#if $current.outTemp.raw > 26.7
 <div id="fzeie">
 #if $current.heatindex.raw > 26.7 and $current.heatindex.raw < 33
  <p style="background-color: gold"><strong>Vorsicht!!!</strong><br />Erschöpfung möglich bei längerer Aktivität.</p>
 #elif $current.heatindex.raw > 32 and $current.heatindex.raw < 42
  <p style="background-color: lightpink"><strong>Erhöhte Vorsicht!!!</strong><br /> Möglichkeit von Hitzeschäden wie Sonnenstich, Hitzekrampf und Hitzekollaps.</p>
 #elif $current.heatindex.raw > 41 and $current.hestindex.rwa < 55
  <p style="background-color: lightsalmon"><strong>Gefahr!!!</strong><br />Sonnenstich, Hitzekrampf und Hitzekollaps sind wahrscheinlich; Hitzeschlag ist möglich.</p>
 #elif $current.heatindex.raw > 54
  <p style="background-color: hotpink"><strong>Erhöhte Gefahr!!!</strong><br />Hitzschlag und Sonnenstich sind wahrscheinlich bei längerem Aufenthalt</p>
 #end if
 </div>
#end if


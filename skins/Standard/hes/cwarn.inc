#encoding UTF-8
## cwarn.inc 2015-02-23 18:24:18Z hes $


#if $current.outTemp.raw is not None
   #if $current.outTemp.raw > 26.7
   <div id="fzeie">
     #if $current.heatindex.raw > 26.7 and $current.heatindex.raw < 33.0
         <p style="background-color: gold"><strong>Vorsicht!!!</strong><br />Erschöpfung möglich bei längerer Aktivität.</p>
     #elif $current.heatindex.raw > 32.0 and $current.heatindex.raw < 42.0
         <p style="background-color: lightpink"><strong>Erhöhte Vorsicht!!!</strong><br /> Möglichkeit von Hitzeschäden wie Sonnenstich, Hitzekrampf und Hitzekollaps.</p>
     #elif $current.heatindex.raw > 41.0 and $current.hestindex.rwa < 55.0
         <p style="background-color: lightsalmon"><strong>Gefahr!!!</strong><br />Sonnenstich, Hitzekrampf und Hitzekollaps sind wahrscheinlich; Hitzeschlag ist möglich.</p>
     #elif $current.heatindex.raw > 54.0
         <p style="background-color: hotpink"><strong>Erhöhte Gefahr!!!</strong><br />Hitzschlag und Sonnenstich sind wahrscheinlich bei längerem Aufenthalt</p>
     #end if
   </div>
  #end if
#end if

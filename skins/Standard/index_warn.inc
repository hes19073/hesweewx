#encoding UTF-8
##  index_warn.inc 2749 2020-08-30 14:15:24Z hes $
## Wetterwarnungen des DWD nach Landkreisen
##
##import datetime
#if len($warn_kopf) > 3
#set $warnstufe = str($warn_level) + '.png'
<div id="fzeie">
  <ul>
   <li><img src=$warnstufe width='28' height='18' alt='level' />&nbsp;$warn_kopf&nbsp;<img src=$warnstufe width='28' height='18' alt='level' />
       Deutscher Wetterdienst Warnung <b>gültig vom:&nbsp;$warn_start&nbsp;Uhr bis&nbsp;$warn_end&nbsp;Uhr</b></li>
   <li>$warn_meldung</li>
 #if len($warn_inst) > 2
   <li>$warn_inst</li>
 #end if
  </ul> 
</div>
#end if


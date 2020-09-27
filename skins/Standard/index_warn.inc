#encoding UTF-8
##  index_warn.inc 2749 2020-08-30 14:15:24Z hes $
## Wetterwarnungen des DWD nach Landkreisen
##
#import datetime
#if len($warn_kopf) > 3
#set $warnstufe = str($warn_level) + '.png'
#set $ts_start = datetime.datetime.fromtimestamp($warn_start).strftime('%d.%m.%Y %H:%M')
#set $ts_end = datetime.datetime.fromtimestamp($warn_end).strftime('%d.%m.%Y %H:%M')
<div id="fzeie">
  <ul>
   <li><img src=$warnstufe width='28' height='18' alt='level' />&nbsp;$warn_kopf&nbsp;<img src=$warnstufe width='28' height='18' alt='level' />
       Deutscher Wetterdienst Wetterwarnung vom:&nbsp;$warn_update&nbsp;gültig vom:&nbsp;$ts_start&nbsp;Uhr bis&nbsp;$ts_end&nbsp;Uhr</li>
   <li>$warn_meldung</li>
 #if len($warn_inst) > 2
   <li>$warn_inst</li>
 #end if
  </ul> 
</div>
#end if


## for weewx - Copyright 2017- Hartmut Schweidler
## DayorNight.inc  2017-10-11 13:53:34Z hes $
#errorCatcher Echo
#encoding UTF-8

#set $sunrise_ts = $almanac.sun.rise.raw
#set $sunset_ts = $almanac.sun.set.raw
#set $now_ts = $current.dateTime.raw

<p>

#if $sunrise_ts < $now_ts and $now_ts < $sunset_ts
    #set $seconds = $now_ts - $sunrise_ts
    #set $HouMin = $seconds
    #set $hours = $seconds //3600
    #set $seconds %= 3600
    #set $minutes = $seconds//60
    #set $seconds %= 60
    #if $HouMin < 3600
         Tageslicht seit <b>$("%d Minuten und %d Sekunden " % ($minutes, $seconds))
    #else
         Tageslicht seit <b>$("%d Stunden und %d Minuten " % ($hours, $minutes))
    #end if
#else 
    #set $seconds = $sunrise_ts - $now_ts 
    #set $HouMin = $seconds
    #set $hours = $seconds //3600
    #set $seconds %= 3600
    #set $minutes = $seconds//60

    #if $HouMin < 3600
         Nacht seit <b>$("%d Minuten " % ($minutes))
    #else
         Nacht seit <b>$("%d Stunden und %d Minuten " % ($hours, $minutes))
    #end if
#end if

</b>am Standort der privaten Wetterstation&nbsp;$station.location </p>

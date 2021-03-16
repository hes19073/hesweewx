#encoding UTF-8
## Day astronomical tags/calculations
##
## apt-get install python3-relativedelta
## 
## Heute ist der 197 Tag des Jahres  2020  .
## Aktuell ist es Tag und bisher gab es 1,5 Stunden Sonnenschein.
## Die theoretische oder astronomische Sonnenscheindauer beträgt heute  16 Stunden, 32 Minuten und 17 Sekunden,
## dass sind 145 Sekunden weniger als Gestern oder 2 Minuten und 25 Sekunden.
## Mit Blick auf die Sommersonnenwende am 20.06.2020 sind das 32 Minuten und 14 Sekunden 
## weniger Tageslicht,
## oder anders ausgedrückt, die Sonne geht heute
## 17 Minuten und 7 Sekunden später auf und 15 Minuten und 7 Sekunden früher unter.
## Die berechneten Zeitangaben beziehen sich auf den geographischen Standort der Wetterstation 
## Klein Rogahn bei 53° 36.36' N und 011° 20.48' O, 53.4 m über Normalhöhennull (m ü-NHN).

#import time
#set $now = $current.dateTime.raw
#set $timenow = $time.time()
#set $oldday = $now - 24 * 3600

## now day or night
## ist jetzt Tag oder Nacht

#if ($timenow > $almanac.sun.rise.raw) and ($timenow < $almanac.sun.set.raw)
    #set $dayornight = "Tag"
#else
    #set $dayornight = "Nacht"
#end if

## moonAge and moonDays calculations for the day
## das Mondalter und die Mond Tage

#set $moonAge = $time.gmtime($now - $almanac.previous_new_moon.raw)
#set $moonDays = int(round(($now - $almanac.previous_new_moon.raw) / 86400, 0))

## calculations the next update for the webpage
## Aktualisierung der Webseiten

#set $timeFormat = "%H:%M"
#try
    #set $timenextupdate = time.strftime($timeFormat,time.localtime($time.time() + float($current.interval.raw) * 60))
#except
    #set $timenextupdate = 0
#end try

## now calculation time difference daylight for summer and winter
## Stunden, Minuten und Sekunden Tageslicht heute, gestern und Differenz

#set $today_daylight = $almanac.sun.set.raw -  $almanac.sun.rise.raw
#set $daysec = $today_daylight
#set $dayhours = $daysec // 3600
#set $daysec %= 3600
#set $dayminutes = $daysec // 60
#set $daysec %= 60

#set $oldday_daylight = $almanac($almanac_time=$oldday).sun.set.raw - $almanac($almanac_time=$oldday).sun.rise.raw
#set $daydifference = $today_daylight - $oldday_daylight
#set $olddifference = $oldday_daylight - $today_daylight

#set $daysecD = $daydifference
#set $daydh = $daysecD // 3600
#set $daysecD %= 3600
#set $daydm = $daysecD // 60
#set $daysecD %= 60

#set $oldsecD = $olddifference
#set $olddh = $oldsecD // 3600
#set $oldsecD %= 3600
#set $olddm = $oldsecD // 60
#set $oldsecD %= 60

## winter or summer solstice diff to now
## Wintersonnenwende oder Sommersonnenwende

#if $almanac.previous_winter_solstice.raw > $almanac.previous_summer_solstice.raw
    #set $daywiso = $almanac.previous_winter_solstice.raw
#else
    #set $daywiso = $almanac.previous_summer_solstice.raw
#end if

## winter or summer solstice daylight diff
## Wintersonnenwende oder Sommersonnenwende Zeit Differenz zu heute

#set $daywiso_daylight = $almanac($almanac_time=$daywiso).sun.set.raw - $almanac($almanac_time=$daywiso).sun.rise.raw

#set $diffWinter = $today_daylight - $daywiso_daylight
#set $diffSommer = $daywiso_daylight - $today_daylight

#set $wisosec = $diffWinter 
#set $wisodh = $wisosec // 3600
#set $wisosec %= 3600
#set $wisodm = $wisosec // 60
#set $wisosec %= 60

#set $sowisec = $diffSommer
#set $sowidh = $sowisec // 3600
#set $sowisec %= 3600
#set $sowidm = $sowisec // 60
#set $sowisec %= 60

## time for sunset and sunrise difference
## Zeit Differenz Sonnenauf- bzw. -untergang zu Winter- bzw. Sommersonnenwende

#from datetime import datetime
#from dateutil.relativedelta import relativedelta

#set $t_a_r = datetime.fromtimestamp($almanac($almanac_time=$daywiso).sun.rise.raw)
#set $t_b_r = datetime.fromtimestamp($almanac.sun.rise.raw)
#set $t_a_s = datetime.fromtimestamp($almanac($almanac_time=$daywiso).sun.set.raw )
#set $t_b_s = datetime.fromtimestamp($almanac.sun.set.raw)

#if $almanac.previous_winter_solstice.raw > $almanac.previous_summer_solstice.raw

#set $t_diff_Rise = relativedelta($t_b_r, $t_a_r)     ## later/end time comes first!
#set $diffRisedh = $t_diff_Rise.hours
#set $diffRisedm = $t_diff_Rise.minutes
#set $diffRisesec = $t_diff_Rise.seconds

#set $t_diff_Set = relativedelta($t_b_s, $t_a_s)      ## later/end time comes first!
#set $diff_Setdh = $t_diff_Set.hours
#set $diff_Setdm = $t_diff_Set.minutes
#set $diff_Setsec = $t_diff_Set.seconds

#else

#set $t_diff_Rise = relativedelta($t_b_r, $t_a_r)     ## later/end time comes first!
#set $diffRisedh = 23 - $t_diff_Rise.hours
#set $diffRisedm = 59 - $t_diff_Rise.minutes
#set $diffRisesec = 59 - $t_diff_Rise.seconds

#set $t_diff_Set = relativedelta($t_b_s, $t_a_s)      ## later/end time comes first!
#set $diff_Setdh = $t_diff_Set.hours
#set $diff_Setdm = $t_diff_Set.minutes
#set $diff_Setsec = $t_diff_Set.seconds

#end if

<p>
Heute ist der<b>&nbsp;$current.dateTime.format("%j")&nbsp;</b>Tag des Jahres
<b>&nbsp;$current.dateTime.format("%Y")</b>
##if len($day00) > 3
##     und es ist: <b>$day00</b>&nbsp;.
##else
##    &nbsp;.
##end if
<br />

Aktuell ist es <b>$dayornight</b>
#if $dayornight == "Tag"
    und bisher gab es
    #if $day.sunshineS.sum.hour.raw > 0.0
        <b>$day.sunshineS.sum.hour&nbsp;</b>
    #else
        keinen
    #end if
    Sonnenschein.
#else
    am Standort.
#end if
</p>

<hr />
<p>
Die theoretische oder astronomische Sonnenscheindauer beträgt heute
<b>$("%d Stunden, %d Minuten und %d Sekunden," % ($dayhours, $dayminutes, $daysec))</b>
<br/> dass sind
#if $daydifference > 0
 #if $daydifference < 60 
    <b> $("%d Sekunden " % $daydifference) mehr </b>als Gestern.
 #else 
    <b> $("%d Sekunden " % $daydifference) mehr </b>als Gestern oder
    <b> $("%d Minuten und %d Sekunden." % ($daydm, $daysecD))</b>
 #end if
#else
 #if $olddifference < 60 
    <b> $("%d Sekunden " % $olddifference) weniger </b>als Gestern.
 #else
    <b> $("%d Sekunden " % $olddifference) weniger </b>als Gestern oder
    <b> $("%d Minuten und %d Sekunden." % ($olddm, $oldsecD))</b>
 #end if
#end if
</p>

<p>Mit Blick auf die
#if $diffWinter  > 0
    Wintersonnenwende am $almanac.previous_winter_solstice.format("%d.%m.%Y")
    sind das
    #if $diffWinter  < 60
        <b> $("%d Sekunden " % ($wisosec))
    #elif $diffWinter  < 3600
        <b> $("%d Minuten und %d Sekunden " % ($wisodm, $wisosec))
    #else
        <b> $("%d Stunden, %d Minuten und %d Sekunden " % ($wisodh, $wisodm, $wisosec))
    #end if
    mehr</b>
#else
    Sommersonnenwende am $almanac.previous_summer_solstice.format("%d.%m.%Y")
    sind das
    #if $diffSommer < 60
        <b>$("%d Sekunden " % ($sowisec))
    #elif $diffSommer < 3600
        <b>$("%d Minuten und %d Sekunden " % ($sowidm, $sowisec))
    #else
        <b>$("%d Stunden, %d Minuten und %d Sekunden " % ($sowidh, $sowidm, $sowisec))
    #end if
    weniger</b>
#end if
    Tageslicht.
</p>    
   
<p>
#if $diffWinter  > 0
    Am $almanac.previous_winter_solstice (Wintersonnenwende)
#else
    Am $almanac.previous_summer_solstice (Sommersonnenwende)
#end if  

ging die Sonne um $almanac($almanac_time=$daywiso).sun.rise Uhr auf und 
um $almanac($almanac_time=$daywiso).sun.set Uhr unter,<br /> 
heute geht die Sonne um $almanac.sun.rise Uhr auf und 
um $almanac.sun.set Uhr unter.<br />

Die Sonne geht heute 

#if $diffWinter > 0

    #if $diffRisedh < 1
        $("%d Minuten und %d Sekunden " % ($diffRisedm, $diffRisesec))
    #else
        $("%d Stunden, %d Minuten und %d Sekunden " % ($diffRisedh, $diffRisedm, $diffRisesec))
    #end if

    <b>früher</b> auf und

    #if $diff_Setdh < 1
        $("%d Minuten und %d Sekunden " % ($diff_Setdm, $diff_Setsec))
    #else
        $("%d Stunden, %d Minuten und %d Sekunden " % ($diff_Setdh, $diff_Setdm, $diff_Setsec))
    #end if

    <b>später</b> unter.<br />

#else

    #if $diffRisedh < 1
        $("%d Minuten und %d Sekunden " % ($diffRisedm, $diffRisesec))
    #else
        $("%d Stunden, %d Minuten und %d Sekunden " % ($diffRisedh, $diffRisedm, $diffRisesec))
    #end if

    <b>später</b> auf und

    #if $diff_Setdh < 1
        $("%d Minuten und %d Sekunden " % ($diff_Setdm, $diff_Setsec))
    #else
        $("%d Stunden, %d Minuten und %d Sekunden " % ($diff_Setdh, $diff_Setdm, $diff_Setsec))
    #end if

    <b>früher</b> unter.<br />

#end if

<br><small>Die berechneten Zeiten beziehen sich auf den geographischen Standort der Wetterstaton $station.location
bei&nbsp;$station.latitude[0]&deg; $station.latitude[1]' $station.latitude[2]&nbsp;,
&nbsp;$station.longitude[0]&deg; $station.longitude[1]' $station.longitude[2]&nbsp;und
&nbsp;$station.altitude&nbsp;über Normalhöhennull (m ü. NHN).</small>
</p>



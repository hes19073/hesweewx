#encoding UTF-8
##Day astronomical tags/calculations
##
#import time
#set $now = $current.dateTime.raw
#set $timenow = $time.time()
#set $oldday = $now - 24*3600

#if ($timenow > $almanac.sun.rise.raw) and ($timenow < $almanac.sun.set.raw)
    #set $dayornight = "Tag"
#else
    #set $dayornight = "Nacht"
#end if

#set $moonAge = $time.gmtime($now - $almanac.previous_new_moon.raw)
#set $moonDays = int(round(($now - $almanac.previous_new_moon.raw)/86400,0))

#set $timeFormat = "%H:%M"
#try
    #set $timenextupdate=time.strftime($timeFormat,time.localtime($time.time() + float($current.interval.raw)*60))
#except
    #set $timenextupdate = 0
#end try

#set $today_daylight = $almanac.sun.set.raw -  $almanac.sun.rise.raw
#set $daysec = $today_daylight
#set $dayhours = $daysec //3600
#set $daysec %= 3600
#set $dayminutes = $daysec//60
#set $daysec %= 60

#set $oldday_daylight = $almanac($almanac_time=$oldday).sun.set.raw - $almanac($almanac_time=$oldday).sun.rise.raw
#set $daydifference = $today_daylight - $oldday_daylight
#set $olddifference = $oldday_daylight - $today_daylight

#set $daysecD = $daydifference
#set $daydh = $daysecD //3600
#set $daysecD %= 3600
#set $daydm = $daysecD //60
#set $daysecD %= 60

#set $oldsecD = $olddifference
#set $olddh = $oldsecD //3600
#set $oldsecD %= 3600
#set $olddm = $oldsecD //60
#set $oldsecD %= 60


#if $almanac.previous_winter_solstice.raw > $almanac.previous_summer_solstice.raw
    #set $daywiso = $almanac.previous_winter_solstice.raw
#else
    #set $daywiso = $almanac.previous_summer_solstice.raw
#end if

#set $today_daylight = $almanac.sun.set.raw -  $almanac.sun.rise.raw
#set $daywiso_daylight = $almanac($almanac_time=$daywiso).sun.set.raw - $almanac($almanac_time=$daywiso).sun.rise.raw

#set $diffWinter = $today_daylight - $daywiso_daylight
#set $diffSommer = $daywiso_daylight - $today_daylight

#set $wisosec = $diffWinter
#set $wisodh = $wisosec //3600
#set $wisosec %= 3600
#set $wisodm = $wisosec //60
#set $wisosec %= 60

#set $sowisec = $diffSommer
#set $sowidh = $sowisec //3600
#set $sowisec %= 3600
#set $sowidm = $sowisec //60
#set $sowisec %= 60

<p>Heute ist der<b>&nbsp;$current.dateTime.format("%j")&nbsp;</b>Tag des Jahres
<b>&nbsp;$current.dateTime.format("%Y")&nbsp;</b>
#if len($day00) > 3
     und es ist <b>$day00 .</b>
#end if
<br />

Aktuell ist es <b>$dayornight</b>
#if $dayornight == "Tag"
    #if $day.sunshineS.sum.hour.raw > 0.0
        und bisher gab es <b>$day.sunshineS.sum.hour&nbsp;</b>Sonnenschein.
    #else
        und bisher war die Sonne hinter Wolken.
    #end if
#else
    am Standort.
#end if
<br />
Die theoretische oder astronomische Sonnenscheindauer beträgt Heute&nbsp;
<b>$("%d Stunden, %d Minuten und %d Sekunden" % ($dayhours, $dayminutes, $daysec))</b>
,<br/> dass sind
#if $daydifference > 0
    <b> $("%d Sekunden " % $daydifference)</b> mehr als Gestern oder
    <b> $("%d Minuten und %d Sekunden," % ($daydm, $daysecD))</b><br />
#else
    <b> $("%d Sekunden " % $olddifference)</b> weniger als Gestern oder
    <b> $("%d Minuten und %d Sekunden," % ($olddm, $oldsecD))</b><br />
#end if

#if $diffWinter > 0
    bezogen auf die Wintersonnenwende am $almanac.previous_winter_solstice.format("%d.%m.%Y")
    sind das
    #if $diffWinter < 3600
        <b> $("%d Minuten und %d Sekunden " % ($wisodm, $wisosec))</b>
    #else
        <b> $("%d Stunden, %d Minuten und %d Sekunden " % ($wisodh, $wisodm, $wisosec))</b>
    #end if
        <i>mehr</i>
#else
    bezogen auf die Sommersonnenwende am $almanac.previous_summer_solstice.format("%d.%m.%Y")
    sind das
    #if $diffSommer < 3600
        <b> $("%d Minuten und %d Sekunden " % ($sowidm, $sowisec))</b>
    #else
        <b> $("%d Stunden, %d Minuten und %d Sekunden " % ($sowidh, $sowidm, $sowisec))</b>
    #end if
        <i>weniger</i>
#end if
    Tageslicht.
</p>

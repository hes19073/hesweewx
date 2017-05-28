#encoding UTF-8
        <div id="hes">  <!-- align="center"> -->
      #set $now = $current.dateTime.raw
      #if $almanac.previous_winter_solstice.raw > $almanac.previous_summer_solstice.raw
           #set $yeste = $almanac.previous_winter_solstice.raw
      #else
           #set $yeste = $almanac.previous_summer_solstice.raw
      #end if
      #set $today_daylight = $almanac.sun.set.raw -  $almanac.sun.rise.raw
      #set $yeste_daylight = $almanac($almanac_time=$yeste).sun.set.raw - $almanac($almanac_time=$yeste).sun.rise.raw
      #set $difference = $today_daylight - $yeste_daylight
      #set $seconds = $almanac.sun.set.raw - $almanac.sun.rise.raw
      #set $hours = $seconds //3600
      #set $seconds %= 3600
      #set $minutes = $seconds//60
      #set $seconds %= 60

      #set $difhes = $difference
      #set $dh = $difhes //3600
      #set $difhes %= 3600
      #set $dm = $difhes //60
      #set $difhes %= 60

      #set $difhes1 = -$difference
      #set $dh1 = $difhes1 //3600
      #set $difhes1 %= 3600
      #set $dm1 = $difhes1 //60
      #set $difhes1 %= 60
    <p>
      #if $difference > 0
          bezogen auf die Wintersonnenwende am $almanac.previous_winter_solstice.format("%d.%m.%Y")
          #if $difference < 3600
              sind das <b> $("%d Minuten und %d Sekunden " % ($dm, $difhes))</b>mehr Tageslicht.</p>
          #else
              sind das <b> $("%d Stunden, %d Minuten und %d Sekunden " % ($dh, $dm, $difhes))</b>mehr Tageslicht.</p>
          #end if
      #else
          dass sind <b> $("%d Sekunden weniger als Gestern " % -$difference) </b>oder<b> $("%d Minuten und %d Sekunden." % ($dm1, $difhes1))</b></p>
      #end if
     </div>



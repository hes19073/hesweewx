#encoding UTF-8
## link.inc 2749 2015-01-06 18:15:24Z hes $

<div id='header'>
 <div id="masthead">
  <h1>Wetterstation&nbsp;$station.location</h1>
  <p>Breitengrad:&nbsp;$station.latitude[0]&deg; $station.latitude[1]'
       $station.latitude[2]&nbsp;&brvbar;&nbsp;
      L&auml;ngengrad:&nbsp;$station.longitude[0]&deg;
      $station.longitude[1]' $station.longitude[2]&nbsp;&brvbar;&nbsp;
      H&ouml;he:&nbsp;$station.altitude</p>
  <h2>Aktuelle Messwerte am&nbsp;$current.dateTime&nbsp;Uhr</h2>

<div class='hesmo'>
  <ul>
   <li>Mond&nbsp;&#8679;&nbsp;$almanac.moon.rise</li>
   <li>Mond&nbsp;&#8681;&nbsp;$almanac.moon.set</li>
   <li>$almanac.moon_phase&nbsp;$almanac.moon_fullness%</li>
  </ul>
</div> <!-- ende Mond -->

<div class='hesso'>
   #set $sunrise_ts = $almanac.sun.rise.raw
   #set $sunset_ts = $almanac.sun.set.raw
   #set $daylight_s = $sunset_ts - $sunrise_ts
   #set $daylight_hours = int($daylight_s / 3600)
   #set $daylight_minutes = int(($daylight_s % 3600) / 60)
   #set $daylight_h_str = "%02d" % $daylight_hours
   #set $daylight_m_str = "%02d" % $daylight_minutes

    <ul>
     <li>Sonne&nbsp;&#8679;&nbsp;$almanac.sun.rise</li>
     <li>Sonne&nbsp;&#8681;&nbsp;$almanac.sun.set</li>
     <li>Tageslicht:&nbsp;$daylight_h_str:$daylight_m_str</li>
    </ul>
</div> <!-- ende sonne  -->
<div class="navbar">
 <input type="button" value=" WX-2013 " onclick="openURL('index.html')" />
 <input type="button" value=" OWFS-Sen " onclick="openURL('index2.html')" />
 <input type="button" value=" Server  " onclick="openURL('server.html')" />
 <input type="button" value=" Prognose " onclick="openURL('forecast.html')" />
 <input type="button" value=" Jahre Temperaturen " onclick="openURL('temp.html')" />
 <input type="button" value=" Jahre Wind/Böen/Weg " onclick="openURL('wind.html')" />
 <input type="button" value=" Jahre Niederschlag " onclick="openURL('rain.html')" />
 <input type="button" value=" Statistik " onclick="openURL('statistik.html')" />
 <input type="button" value=" Tabelle/ Woche " onclick="openURL('week-table.html')" />
 <input type="button" value=" Tabelle/ 7 Tage " onclick="openURL('week-table-last.html')" />
 <input type="button" value=" Tabelle/ 30 Tage " onclick="openURL('thirty-day.html')" />
 <input type="button" value=" Tabelle/ Monat " onclick="openURL('month-table.html')" />
 <hr />
 #for $monthYear in $SummaryByMonth
     #set $hesweb = "Archiv/KR-" + $monthYear + "-table.html"
     #set $heslis = $monthYear
     <input type="button" value="$heslis" onclick="openURL('$hesweb')" />
 #end for
 <hr />
 #for $yr in $SummaryByYear
     #set $hesweby = "Archiv/KR-" + $yr + "-table.html"
     #set $heslisy = $yr
     <input type="button" value="$heslisy" onclick="openURL('$hesweby')" />
 #end for
</div>

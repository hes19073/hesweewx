## for weewx - Copyright 2015- Hartmut Schweidler
## header.inc  2015-05-02 20:53:34Z hes $
#errorCatcher Echo
#encoding UTF-8

##Chandler Burning Index calculations
#try
    #set $cbi = round((((110 - 1.373 * $current.outHumidity.raw) - 0.54 * (10.20 - $current.outTemp.raw)) * (124 * 10**(-0.0142 * $current.outHumidity.raw)))/60,1)
#except
    #set $cbi = 0
#end try
#if ($cbi > 97.5)
    #set $cbitext = "EXTREM"
    #set $cbifarb = '#FF0000'
#elif ($cbi >= 90)
    #set $cbitext = "SEHR HOCH"
    #set $cbifarb = '#ffa500'
#elif ($cbi >= 75)
    #set $cbitext = "HOCH"
    #set $cbifarb = '#ffff00'
#elif ($cbi >= 50)
    #set $cbitext = "NORMAL"
    #set $cbifarb = '#66cdaa'
#else
    #set $cbitext="GERING"
    #set $cbifarb = '#00ff00'
#end if
#######################################################
##HeatColorWord calculations
##
#set $chillC = $current.windchill.raw
#set $humidexC = $current.humidex.raw
#set heatColorWords = ['Unknown', 'EXTREME Hitze', 'gefährliche Hitze', 'extreme Hitze', 'extreme Wärme', 'Hitze/Heiß', 'heiß', 'warm', 'angenehm', 'kühl', 'kalt', 'empfindlich kalt', 'sehr kalt', 'extrem kalt']
#set hcwfarbs = ['', 'color: white; background-color: #BA1928;', 'color: white; background-color: #E02538;', '', 'color: black; background-color: #E178A1;', '', 'color: white; background-color: #CC6633;', 'color: black; background-color: #CC9933;', 'color: black; background-color: #C6EF8C;', 'color: black; background-color: #89B2EA;', 'color: white; background-color: #6699FF;', 'color: white; background-color: #3366FF;', 'color: white; background-color: #806AF9;', 'color: black; background-color: #91ACFF;']
#set $heatColorWord = heatColorWords[0]
#if $current.outTemp.raw is not None
    #if ($current.outTemp.raw > 32)
        #if ($humidexC is not None)
            #if ($humidexC > 54)
                #set $heatColorWord = heatColorWords[1]
                #set $hcwfarb = hcwfarbs[1]
            #elif ($humidexC > 45)
                #set $heatColorWord = heatColorWords[2]
                #set $hcwfarb = hcwfarbs[2]
            #elif ($humidexC > 39)
                #set $heatColorWord = heatColorWords[4]
                #set $hcwfarb = hcwfarbs[4]
            #elif ($humidexC > 29)
                #set $heatColorWord = heatColorWords[6]
                #set $hcwfarb = hcwfarbs[6]
            #end if
        #else
            #set $heatColorWord = heatColorWords[0]
            #set $hcwfarb = hcwfarbs[0]
        #end if
    #elif ($chillC is not None)
        #if ($chillC < 16)
            #if ($chillC < -18)
                #set $heatColorWord = heatColorWords[13]
                #set $hcwfarb = hcwfarbs[13]
            #elif ($chillC < -9)
                #set $heatColorWord = heatColorWords[12]
                #set $hcwfarb = hcwfarbs[12]
            #elif ($chillC < -1)
                #set $heatColorWord = heatColorWords[11]
                #set $hcwfarb = hcwfarbs[11]
            #elif ($chillC < 8)
                #set $heatColorWord = heatColorWords[10]
                #set $hcwfarb = hcwfarbs[10]
            #elif ($chillC < 16)
                #set $heatColorWord = heatColorWords[9]
                #set $hcwfarb = hcwfarbs[9]
            #end if
        #elif (($chillC >= 16) and ($current.outTemp.raw <= 32))
            #if ($current.outTemp.raw < 26)
                #set $heatColorWord = heatColorWords[8]
                #set $hcwfarb = hcwfarbs[8]
            #else
                #set $heatColorWord = heatColorWords[7]
                #set $hcwfarb = hcwfarbs[7]
            #end if
        #else
            #set $heatColorWord = heatColorWords[0]
            #set $hcwfarb = hcwfarbs[0]
        #end if
    #else
        #set $heatColorWord = heatColorWords[0]
        #set $hcwfarb = hcwfarbs[0]
    #end if
#else
    #set $heatColorWord = heatColorWords[0]
    #set $hcwfarb = hcwfarbs[0]
#end if


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
  <li>Brandgefahr</li>
  <li style="background-color: $cbifarb" >$cbi&nbsp;/&nbsp;100&nbsp;</li>
  <li style="background-color: $cbifarb" >$cbitext</li>
 </ul>
</div> <!-- ende Mond -->

<div class='hesso'>
  <ul>
   <li>Heute</li>
   <li style=" $hcwfarb">&nbsp;$current.outTemp</li>
   <li style=" $hcwfarb">$heatColorWord</li>
  </ul>
</div> <!-- ende sonne  -->
 
<div class="navbar">
 <ul id="nav">
  <li><input type="button" value=" Aktuell " onclick="openURL('index.html')" /></li>
  <li><input type="button" value=" OWFS " onclick="openURL('index2.html')" /></li>
  <!-- <li><input type="button" value=" WH-3080 " onclick="openURL('inWX3080.html')" /></li> -->
  <li><input type="button" value=" Heute/ Tag " onclick="openURL('day.html')" /></li>
  <li><input type="button" value="  Prognose  " onclick="openURL('forecast.html')" />
   <ul>
    <li><input type="button" value=" Prognose-weewx " onclick="openURL('forecast.html')" /></li>
    <li><input type="button" value="  WU-Prognose   " onclick="openURL('forecastkr.html')" /></li>
    <li><input type="button" value="  IMECKLEN20    " onclick="openURL('http://www.wunderground.com/cgi-bin/findweather/hdfForecast?query=53.606%2C11.341&amp;sp=IMECKLEN20')" /></li>
   </ul>
  </li>
  <li><input type="button" value="   Station   " onclick="openURL('station.html')" />
   <ul>
    <li><input type="button" value=" Wetterstation " onclick="openURL('station.html')" /></li>
    <li><input type="button" value=" Wetterbilder  " onclick="openURL('wetter.html')" /></li>
    <li><input type="button" value=" Wetterserver  " onclick="openURL('server.html')" /></li>
    <li><input type="button" value=" Astronomie " onclick="openURL('astro.html')" /></li>
   </ul>
  </li>
  <li><input type="button" value="  Statistik  " onclick="openURL('statistik.html')" />
   <ul>
    <li><input type="button" value=" Die Woche " onclick="openURL('week.html')" /></li>
    <li><input type="button" value=" Der Monat " onclick="openURL('month.html')" /></li>
    <li><input type="button" value=" Das Jahr_ " onclick="openURL('year.html')" /></li>
    <li><input type="button" value=" Rekorde__ " onclick="openURL('alltime.html')" /></li>
    <li><input type="button" value=" Temperatur " onclick="openURL('temp.html')" /></li>
    <li><input type="button" value=" Niederschlag " onclick="openURL('rain.html')" /></li>
    <li><input type="button" value=" Wind Böen " onclick="openURL('wind.html')" /></li>
    <li><input type="button" value=" Tabellen >> " onclick="openURL('week-table.html')" />
     <ul>
      <li><input type="button" value=" Die Woche " onclick="openURL('week-table.html')" /></li>
      <li><input type="button" value="  7 Tage   " onclick="openURL('week-table-last.html')" /></li>
      <li><input type="button" value=" 30 Tage   " onclick="openURL('thirty-day.html')" /></li>
      <li><input type="button" value=" Der Monat >>" onclick="openURL('month-table.html')" />
       <ul>
         #for $monthYear in $SummaryByMonth
            #set $hesweb = "Archiv/KR-" + $monthYear + "-table.html"
            #set $heslis = $monthYear
            <li><input type="button" value="$heslis" onclick="openURL('$hesweb')" /></li>
         #end for
       </ul>
      </li>
      <li><input type="button" value=" Die Jahre >>" onclick="openURL('year-table.html')" />
       <ul>
         #for $yr in $SummaryByYear
            #set $hesweby = "Archiv/KR-" + $yr + "-table.html"
            #set $heslisy = $yr
            <li><input type="button" value="$heslisy" onclick="openURL('$hesweby')" /></li>
         #end for
       </ul>
      </li>
     </ul>
    </li>
    <li><input type="button" value=" Kalenderjahr " onclick="openURL('year-table.html')" /></li>
   </ul>
  </li>
  <li><input type="button" value=" Wetternetzwerk " onclick="openURL('index.html')" />
   <ul>
    <li><input type="button" value=" wunderground " onclick="openURL('http://www.wunderground.com/weatherstation/WXDailyHistory.asp?ID=IMECKLEN20')" /></li>
    <li><input type="button" value=" PWSweather " onclick="openURL('http://www.pwsweather.com/obs/heskrfrr38.html')" /></li>
    <li><input type="button" value=" CWOP " onclick="openURL('http://www.findu.com/cgi-bin/wxpage.cgi?call=EW3693')" /></li>
    <li><input type="button" value=" WindFinder " onclick="openURL('http://www.windfinder.com/forecast/klein-rogahn')" /></li>
    <li><input type="button" value=" OWM " onclick="openURL('http://openweathermap.org/city/2888316')" /></li>
    <li><input type="button" value=" wetter.com " onclick="openURL('http://www.wetter.com/wetter_aktuell/wetternetzwerk/station/12853/dashboard/')" /></li>
    <li><input type="button" value=" weathercloud " onclick="openURL('http://app.weathercloud.net/d0868076886')" /></li>
   </ul>
  </li>
  <li><input type="button" value=" WEEWX  " onclick="openURL('http://www.weewx.com')" />
   <ul>
    <li><input type="button" value=" weewx-Map " onclick="openURL('http://www.weewx.com/stations')" /></li>
    <li><input type="button" value=" Neuigkeiten " onclick="openURL('http://www.weewx.com/news.html')" /></li>
    <li><input type="button" value=" Dokumente  " onclick="openURL('http://www.weewx.com/docs.html')" /></li>
    <li><input type="button" value=" Daten/Files " onclick="openURL('https://github.com/weewx/weewx')" /></li>
    <li><input type="button" value=" Nutzerforum " onclick="openURL('http://groups.google.com/forum/#!forum/weewx-user')" /></li>
    <li><input type="button" value=" Entwicklung " onclick="openURL('http://groups.google.com/forum/#!forum/weewx-development')" /></li>
   </ul>
  </li>
  <li><input type="button" value="  RSS  " onclick="openURL('RSS/weewx_rss.xml')" /></li>
  <li><input type="button" value=" Ansicht " onclick="openURL('mobile.html')" />
   <ul>
    <li><input type="button" value=" Mobilphone " onclick="openURL('mobile.html')" /></li>
    <li><input type="button" value=" Smartphome " onclick="openURL('smartphone/index.html')" /></li>
   </ul>
  </li>
  <li><input type="button" value=" Impressum " onclick="openURL('http://blog.hes61.de/?page_id=111')" />
   <ul>
    <li><input type="button" value=" Impressum " onclick="openURL('http://blog.hes61.de/?page_id=111')" /></li>
    <li><input type="button" value=" Datenschutz " onclick="openURL('http://blog.hes61.de/datenschutz/')" /></li>
   </ul>
  </li>
</ul>

 <select NAME=noaaselect onchange="openNoaaFile(value)">
 #for $monthYear in $SummaryByMonth
    <option value="$monthYear">$monthYear</option>
 #end for
    <option selected>- Monat -</option>
    </select>
 
 &#8656;&nbsp;NOAA-Daten-Auswahl:&nbsp;&#8658;
   <select NAME=noaaselect onchange="openNoaaFile(value)">
   #for $yr in $SummaryByYear
      <option value="$yr">$yr</option>
   #end for
      <option selected>- Jahr -</option>
   </select>

   &#8656;&#8656;&nbsp;NOAA-Textdatei&nbsp;&nbsp;Archivdaten&#8658;&#8658;
   <select NAME=archivselect onchange="openArchivFile(value)">
   #for $monthYear in $SummaryByMonth
      <option value="$monthYear">$monthYear</option>
   #end for
      <option selected>- Monat -</option>
   </select>
   &#8656;&nbsp;Archivwerte Auswahl:&nbsp;&#8658;
   <select NAME=archivselect onchange="openArchivFile(value)">
   #for $yr in $SummaryByYear
      <option value="$yr">$yr</option>
   #end for
      <option selected>- Jahr -</option>
   </select>
   </div><!--  End navbar1 -->
  </div><!-- Ende masthead -->
 </div> <!-- Ende header -->

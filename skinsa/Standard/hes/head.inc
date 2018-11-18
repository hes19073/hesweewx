## for weewx - Copyright 2015- Hartmut Schweidler
## header.inc  2015-05-02 20:53:34Z hes $
#errorCatcher Echo
#encoding UTF-8
#import time

#if $latest($data_binding='wdsupp_binding').vantageForecastNumber.has_data
    #set $VPn = $latest($data_binding='wdsupp_binding').vantageForecastNumber.raw
    #set $VPn = int($VPn)
    #set $VPn = str($VPn)
    #if $current.outTemp.raw < 0
        #set $VPnumber = 'xicons/VPnumbers/' + $VPn + 's.gif'
    #else
        #set $VPnumber = 'xicons/VPnumbers/' + $VPn + '.gif'
    #end if
#end if

<div id='header'>
 <div id="masthead">
  <h1>Private Wetterstation&nbsp;$station.location</h1>
  <p>Breitengrad:&nbsp;$station.latitude[0]&deg; $station.latitude[1]'
       $station.latitude[2]&nbsp;&brvbar;&nbsp;
      L&auml;ngengrad:&nbsp;$station.longitude[0]&deg;
      $station.longitude[1]' $station.longitude[2]&nbsp;&brvbar;&nbsp;
      H&ouml;he:&nbsp;$station.altitude&nbsp;&brvbar;&nbsp;
      <a href="http://gpso.de/maps/?z=20;p=53.6061,11.34106,WP01-A;">Map</a>&nbsp;&brvbar;&nbsp;
      </p>
  <h2>Aktuelle Messwerte am&nbsp;$current.dateTime.format("%A"), den&nbsp;$current.dateTime&nbsp;Uhr&nbsp;(Zeitzone: $current.dateTime.format("%Z"))</h2>
<div class='hesmo'>
 <ul>
  <li>Brandgefahr</li>
  <li style="$decorator_color('cbIndex', $current.cbIndex.raw)">$current.cbIndex/&nbsp;100&nbsp;</li>
  <li style="$decorator_color('cbIndex', $current.cbIndex.raw)">$decorator_text('cbIndex', $current.cbIndex.raw)</li>
  <li>&nbsp;</li>
  <li><a href="http://weewx.com/">
      <img style="width: 48px; height: 48px;" alt="weewx" src="weewx.png"  /></a></li>
 </ul>
</div> <!-- ende Brandgefahr -->

<div class='hesso'>
 <ul>
  <li><img style="width: 60px; height: 60px;" alt="Wetter" src="$VPnumber" /></li>
  <li style="$decorator_color('heattemp', $current.appTemp.raw)">&nbsp;$current.appTemp</li>
  <li style="$decorator_color('heattemp', $current.appTemp.raw)">$decorator_text('heattemp', $current.appTemp.raw)</li>
 </ul>
#if $varExists('$day00')
    #if len($day00) > 2.0
  <p class="neon">$day00</p>
    #end if
#end if
</div> <!-- ende Temp Sonne  -->
 
<div class="navbar">
 <ul id="nav">
  <li><input type="button" value=" Aktuell " onclick="openURL('index.html')" />   </li>
  <li><input type="button" value=" OWFS  " onclick="openURL('indexOWFS.html')" /></li>
  <li><input type="button" value=" Boden " onclick="openURL('index1.html')" /></li>
  <li><input type="button" value=" Luft " onclick="openURL('indexAir.html')" /></li>
  <li><input type="button" value=" Rad " onclick="openURL('indexRad.html')" /></li>
  <li><input type="button" value=" GDD " onclick="openURL('index3.html')" />
   <ul>
    <li><input type="button" value=" HeizDD " onclick="openURL('heatdeg.html')" /></li>
    <li><input type="button" value=" KühlDD " onclick="openURL('cooldeg.html')" /></li>
    <li><input type="button" value=" HomeDD " onclick="openURL('homedeg.html')" /></li>
    <li><input type="button" value=" WTG 4°C " onclick="openURL('gdd_4.html')" /></li>
    <li><input type="button" value=" WTG 5°C " onclick="openURL('gdd_5.html')" /></li>
    <li><input type="button" value=" WTG 6°C " onclick="openURL('gdd_6.html')" /></li>
    <li><input type="button" value=" WTG 10°C " onclick="openURL('Cydia/C_growth.html')" /></li>
    <li><input type="button" value=" GLT " onclick="openURL('Cydia/C_green.html')" /></li>
    <li><input type="button" value=" Cydia " onclick="openURL('Cydia/C_pomonella.html')" /></li>
   </ul>
  </li>
  <li><input type="button" value=" Tag " onclick="openURL('day.html')" />
   <ul>
    <li><input type="button" value=" Heute " onclick="openURL('daya.html')" /></li>
    <li><input type="button" value=" Temperatur " onclick="openURL('temp.html')" /></li>
    <li><input type="button" value=" Niederschlag " onclick="openURL('rain.html')" /></li>
    <li><input type="button" value=" Wind Böen " onclick="openURL('wind.html')" /></li>
    <li><input type="button" value=" 24 Stunden " onclick="openURL('trend.html')" /></li>
   <!--  <li><input type="button" value=" wx-obs " onclick="openURL('index.php')" /></li> -->
   </ul>
  </li>
  <li><input type="button" value=" Prognose " onclick="openURL('forecast.html')" />
   <ul>
    <li><input type="button" value=" Prognose Weewx " onclick="openURL('forecastT.html')" /></li>
    <li><input type="button" value=" WetterWarnung  " onclick="openURL('indexWarn.html')" /></li>
    <li><input type="button" value=" Wetter Infos " onclick="openURL('indexInfo.html')" /></li>
    <li><input type="button" value=" WetterWissen " onclick="openURL('wissen.html')" /></li>
    <li><input type="button" value=" ISS &Uuml;berflug " onclick="openURL('indexISS.html')" /></li> 
    <li><input type="button" value="  IMECKLEN20    " onclick="openURL('http://www.wunderground.com/cgi-bin/findweather/hdfForecast?query=53.606%2C11.341&amp;sp=IMECKLEN20')" /></li>
   </ul>
  </li>
  <li><input type="button" value=" Station " onclick="openURL('station.html')" />
   <ul>
    <li><input type="button" value=" Wetterbilder  " onclick="openURL('wetter.html')" /></li>
    <li><input type="button" value=" Wetterserver  " onclick="openURL('server.html')" /></li>
    <li><input type="button" value=" Astronomie " onclick="openURL('astro.html')" /></li>
   </ul>
  </li>
  <li><input type="button" value=" Statistik " onclick="openURL('statistik.html')" />
   <ul>
    <li><input type="button" value=" Die Woche " onclick="openURL('week.html')" /></li>
    <li><input type="button" value=" Der Monat " onclick="openURL('month.html')" /></li>
    <li><input type="button" value=" Das Jahr_ " onclick="openURL('year.html')" /></li>
    <li><input type="button" value=" _ Rekorde " onclick="openURL('alltime.html')" /></li>
    <li><input type="button" value=" Archiv__  " onclick="openURL('archiv.html')" />
     <ul>
      <li><input type="button" value=" Alt-Archiv " onclick="openURL('altarchiv.html')" /></li>
      <li><input type="button" value=" Historisch " onclick="openURL('historisch.html')" /></li>
     </ul>
    </li>
    <li><input type="button" value=" Temperatur " onclick="openURL('temp.html')" /></li>
    <li><input type="button" value=" Niederschlag " onclick="openURL('rain.html')" /></li>
    <li><input type="button" value=" Wind Böen " onclick="openURL('wind.html')" /></li>
    <li><input type="button" value=" Sonnentage " onclick="openURL('sola.html')" /></li>
    <li><input type="button" value=" Tabellen  &#8659;" onclick="openURL('week-table.html')" />
     <ul>
      <li><input type="button" value=" Die Woche " onclick="openURL('week-table.html')" /></li>
      <li><input type="button" value="  7 Tage   " onclick="openURL('week-table-last.html')" /></li>
      <li><input type="button" value=" 30 Tage   " onclick="openURL('thirty-day.html')" /></li>
      <li><input type="button" value=" Der Monat &#8659;" onclick="openURL('month-table.html')" />
       <ul>
         #for $monthYear in $SummaryByMonth
            #set $hesweb = "Archiv/KR-" + $monthYear + "-table.html"
            #set $heslis = $monthYear
            <li><input type="button" value="$heslis" onclick="openURL('$hesweb')" /></li>
         #end for
       </ul>
      </li>
      <li><input type="button" value=" Die Jahre &#8659;" onclick="openURL('year-table.html')" />
       <ul>
         #for $year in $alltime.years
            #set $yr = $year.dateTime.format("%Y")
            #set $hesweby = "Archiv/KR-" + $yr + "-table.html"
            #set $heslisy = $yr
            <li><input type="button" value="$heslisy" onclick="openURL('$hesweby')" /></li>
         #end for
       </ul>
      </li>
     </ul>
    </li>
    <li><input type="button" value=" Kalenderjahr " onclick="openURL('year-table.html')" /></li>
    <li><input type="button" value=" Kalenderjahre " onclick="openURL('yearhc.html')" /></li>
   </ul>
  </li>
  <li><input type="button" value=" Netzwerk " onclick="openURL('graphs.html')" />
   <ul>
    <li><input type="button" value=" wunderground " onclick="openURL('http://www.wunderground.com/weatherstation/WXDailyHistory.asp?ID=IMECKLEN20')" /></li>
    <li><input type="button" value=" PWSweather " onclick="openURL('http://www.pwsweather.com/obs/heskrfrr38.html')" /></li>
    <li><input type="button" value=" CWOP " onclick="openURL('http://www.findu.com/cgi-bin/wxpage.cgi?call=EW3693')" /></li>
    <li><input type="button" value=" WindFinder " onclick="openURL('http://www.windfinder.com/forecast/klein-rogahn')" /></li>
    <li><input type="button" value=" OWM " onclick="openURL('http://openweathermap.org/city/2888316')" /></li>
    <li><input type="button" value=" wetter.com " onclick="openURL('http://www.wetter.com/wetter_aktuell/wetternetzwerk/station/12853/dashboard/')" /></li>
    <li><input type="button" value=" weathercloud " onclick="openURL('http://app.weathercloud.net/d0653105008')" /></li>
    <li><input type="button" value=" AWEKAS " onclick="openURL('http://www.awekas.at/de/instrument.php?id=11042')" /></li>
   </ul>
  </li>
  <li><input type="button" value=" WEEWX " onclick="openURL('http://www.weewx.com')" />
   <ul>
    <li><input type="button" value=" weewx-Map " onclick="openURL('http://www.weewx.com/stations')" /></li>
    <li><input type="button" value=" Neuigkeiten " onclick="openURL('http://www.weewx.com/news.html')" /></li>
    <li><input type="button" value=" Dokumente  " onclick="openURL('http://www.weewx.com/docs.html')" /></li>
    <li><input type="button" value=" Daten/Files " onclick="openURL('https://github.com/weewx/weewx')" /></li>
    <li><input type="button" value=" Nutzerforum " onclick="openURL('http://groups.google.com/forum/#!forum/weewx-user')" /></li>
    <li><input type="button" value=" Entwicklung " onclick="openURL('http://groups.google.com/forum/#!forum/weewx-development')" /></li>
    <li><input type="button" value=" GitHub Hes  " onclick="openURL('https://github.com/hes19073/hesweewx.git')" /></li>
   </ul>
  </li>
  <!-- <li><input type="button" value=" RSS " onclick="openURL('RSS/weewx_rss.xml')" /></li> -->
  <li><input type="button" value=" Ansicht " onclick="openURL('mobile.html')" />
   <ul>
    <li><input type="button" value=" RSS / Abo " onclick="openURL('RSS/weewx_rss.xml')" /></li>
    <li><input type="button" value=" SteelGauge " onclick="openURL('ss/index.html')" /></li>
   <!--  <li><input type="button" value=" New Skins  " onclick="openURL('sc/index.html')" /></li> -->
    <li><input type="button" value=" Mobiltelefon " onclick="openURL('mobile.html')" /></li>
    <li><input type="button" value=" Smartphone " onclick="openURL('smartphone/index.html')" /></li>
   </ul>
  </li>
  <li><input type="button" value=" Impressum " onclick="openURL('http://blog.hes61.de/?page_id=111')" />
   <ul>
    <li><input type="button" value=" Word-Press  " onclick="openURL('http://blog.hes61.de')" /></li>
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
   #for $year in $alltime.years
   #set $yr = $year.dateTime.format("%Y")
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
   #for $year in $alltime.years
   #set $yr = $year.dateTime.format("%Y")
      <option value="$yr">$yr</option>
   #end for
      <option selected>- Jahr -</option>
   </select>
   </div><!--  End navbar1 -->
  </div><!-- Ende masthead -->
 </div> <!-- Ende header -->

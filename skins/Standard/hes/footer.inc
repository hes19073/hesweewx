## weewx-footer for weewx - Copyright 2013-2021 Hartmut Schweidler
##  footer.inc 634 2014-09-08 08:34:04Z hes1 $
## nach Vorlage von mwall $
#encoding UTF-8

#set $gmt_date_st = time.gmtime($current.dateTime.raw)
#set $gmt_date = time.strftime("%d. %b %Y", $gmt_date_st)
#set $gmt_day = time.strftime("%A", $gmt_date_st)
#set $gmt_st = time.gmtime($current.dateTime.raw)
#set $gmt = time.strftime("%H:%M", $gmt_st)

<div id='footer'><footer>

<div style="background-color: gold">
      <p>
      Breitengrad:&nbsp;$station.latitude[0]&deg; $station.latitude[1]'
       $station.latitude[2]&nbsp;&brvbar;&nbsp;
      L&auml;ngengrad:&nbsp;$station.longitude[0]&deg;
      $station.longitude[1]' $station.longitude[2]&nbsp;&brvbar;&nbsp;
      H&ouml;he:&nbsp;$station.altitude&nbsp;ü. NHN&nbsp;&brvbar;&nbsp;
      Erstellt am&nbsp;$gmt_day, $gmt_date - $gmt UTC
      </p>
</div>

<div style="background-color:yellow">
     Start-Wetteraufzeichnung: $db_sttime &nbsp;&nbsp;&#124;&nbsp;&nbsp;
     Datenbanklaufzeit:&nbsp; $db_uptime  &nbsp;&nbsp;<br />&nbsp;&nbsp;
     weewx-Laufzeit:&nbsp; $station.uptime&nbsp;&nbsp;&#124;&nbsp;&nbsp;
     Serverlaufzeit:&nbsp; $station.os_uptime&nbsp;&nbsp;&#124;&nbsp;&nbsp;
     weewx  Version:&nbsp; $station.version<br />
     <hr />
     Wetterstation:&nbsp;$station.hardware&nbsp;&#124;&nbsp;Station 6345CSOV&nbsp;&#124;&nbsp;Station 6345OV&nbsp;&#124;&nbsp;<br />
     Zusatz: forecast; cmon; owfs mit 13 Sensoren; Scheehöhe; DWD-Vorschau; DWD-Warnung&nbsp;&#124;&nbsp;
     digitaler Geigerzähler: GQ GMC-300E Plus&nbsp;&#124;&nbsp;
     Luftmessung: Laser PM2.5 Sensor, Modell: SDS011&nbsp;&#124;&nbsp;
     airQ Pro - Luftanalysator (14 Sensoren)<br />
#if $varExists('$year00')
     <hr />
     Weewx Zeit: $year00
     <br />
#end if
</div>

<p>
#if $Extras.has_key('station_subtitle')
     $Extras.station_subtitle<br />
#end if
<b>Machen Sie niemals wichtige Entscheidungen von den Daten dieser Seiten abhängig!</b><br />
</p>
$gettext("footnote1")&nbsp;<a href="http://weewx.com/">WeeWX</a>&nbsp;$gettext("footnote2")<br />
<hr />

<div class="navbar">
  <p> 
   <input type="button" value=" Aktuell " onclick="openURL('index.html')" />
   <input type="button" value=" Garten " onclick="openURL('indexOWFS.html')" />
   <input type="button" value=" Teiche " onclick="openURL('index2.html')" />
   <input type="button" value=" Boden " onclick="openURL('index1.html')" />
   <input type="button" value=" Air " onclick="openURL('indexAir.html')" />
   <!-- <input type="button" value=" air-Q " onclick="openURL('indexAirQ.html')" /> -->
   <input type="button" value=" Blitz " onclick="openURL('indexRad.html')" />
   <input type="button" value=" GDD " onclick="openURL('index3.html')" />
   <input type="button" value=" Heute " onclick="openURL('day.html')" />
   <input type="button" value=" Prognose " onclick="openURL('forecast.html')" />
   <input type="button" value=" Statistik " onclick="openURL('statistik.html')" />
   <input type="button" value=" Woche " onclick="openURL('week.html')" />
   <input type="button" value=" Monat " onclick="openURL('month.html')" />
   <input type="button" value=" Jahr " onclick="openURL('year.html')" />
   <input type="button" value=" ISS " onclick="openURL('indexISS.html')" />
   <input type="button" value=" Archiv " onclick="openURL('archiv.html')" />

  </p>
   <select NAME=noaaselect onchange="openNoaaFile(value)">
   #for $monthYear in $SummaryByMonth
       <option value="$monthYear">$monthYear</option>
   #end for
       <option selected>- Monat -</option>
   </select>
        
   Auswahl:&nbsp;
   <select NAME=noaaselect onchange="openNoaaFile(value)">
   #for $yr in $SummaryByYear
       <option value="$yr">$yr</option>
   #end for
       <option selected>- Jahr -</option>
  </select>

  Monatsübersicht per
  &#8658;&nbsp;Auswahl:
  <select NAME=archivselect onchange="openArchivFile(value)">
  #for $monthYear in $SummaryByMonth
       <option value="$monthYear">$monthYear</option>
  #end for
       <option selected>- Jahr-Monat -</option>
  </select>
        
 </div> <!-- End class navbar -->
<hr />
<div id="fzei">
<div class="lthes">Copyright &copy; 2013 - $current.dateTime.format("%Y") by Hartmut Schweidler</div>
<div class="rthes">Letzte &Auml;nderung am &nbsp;$current.dateTime</div>
<div class="mit"><a href="http://blog.hes61.de/?page_id=111">&raquo; Impressum &laquo;</a>
                 <a href="http://blog.hes61.de/datenschutz/">&raquo; Datenschutz &laquo;</a>

 </div>
</div>

## Include the Google Analytics code if there is an ID available:
#if $Extras.has_key('googleAnalyticsId')
<script>
  var gaJsHost = (("https:" == document.location.protocol) ? "https://ssl." : "http://www.");
  document.write(unescape("%3Cscript src='" + gaJsHost + "google-analytics.com/ga.js' type='text/javascript'%3E%3C/script%3E"));
</script>
<script>
  try{
  var pageTracker = _gat._getTracker("$Extras.googleAnalyticsId");
  pageTracker._trackPageview();
  } catch(err) {}
</script>
#end if

</footer></div><!-- end id "footer" -->


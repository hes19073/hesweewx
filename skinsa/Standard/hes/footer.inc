## weewx-footer for weewx - Copyright 2013-2014 Hartmut Schweidler
##  footer.inc 634 2014-09-08 08:34:04Z hes1 $
## nach Vorlage von mwall $
#encoding UTF-8
<div id='footer'><footer>

<div style="background-color: gold">
      <p>
      Breitengrad:&nbsp;$station.latitude[0]&deg; $station.latitude[1]'
       $station.latitude[2]&nbsp;&brvbar;&nbsp;
      L&auml;ngengrad:&nbsp;$station.longitude[0]&deg;
      $station.longitude[1]' $station.longitude[2]&nbsp;&brvbar;&nbsp;
      H&ouml;he:&nbsp;$station.altitude
      </p>
</div>

<div style="background-color:yellow">
     Start-Wetteraufzeichnung: $start_time &nbsp;&nbsp;&#124;&nbsp;&nbsp;
     Datenbanklaufzeit:&nbsp; $station.db_uptime&nbsp;&nbsp;<br />&nbsp;&nbsp;
     weewx-Laufzeit:&nbsp; $station.uptime&nbsp;&nbsp;&#124;&nbsp;&nbsp;
     Serverlaufzeit:&nbsp; $station.os_uptime&nbsp;&nbsp;&#124;&nbsp;&nbsp;
     weewx  Version:&nbsp; $station.version<br />
     Wetterstation:&nbsp;$station.hardware&nbsp;&#124;&nbsp;Station 6345CSOV&nbsp;&#124;
     Zusatz: forecast; cmon; owfs mit 13 Sensoren; Scheehöhe; DWD-Vorschau; DWD-Warnung; GQ GMC-300E Plus<br />
#if $varExists('$year00') 
     Weewx Zeit: $year00&nbsp;.
#end if
</div>

<p>
 #if $Extras.has_key('station_subtitle')
     $Extras.station_subtitle<br/>
 #end if
</p>
<hr />

<div class="navbar">
  <p> 
   <input type="button" value="   Aktuell   " onclick="openURL('index.html')" />
   <input type="button" value=" OWFS  " onclick="openURL('indexOWFS.html')" />
   <input type="button" value=" Boden " onclick="openURL('index1.html')" />
   <input type="button" value=" Air   " onclick="openURL('indexAir.html')" />
   <input type="button" value=" Rad   " onclick="openURL('indexRad.html')" />
   <input type="button" value=" GDD   " onclick="openURL('index3.html')" />
   <input type="button" value=" Tag /Heute  " onclick="openURL('day.html')" />
   <input type="button" value="  Prognose   " onclick="openURL('forecastT.html')" />
   <input type="button" value="  Statistik  " onclick="openURL('statistik.html')" />
   <input type="button" value="    Woche    " onclick="openURL('week.html')" />
   <input type="button" value="    Monat    " onclick="openURL('month.html')" />
   <input type="button" value="    Jahr     " onclick="openURL('year.html')" />
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


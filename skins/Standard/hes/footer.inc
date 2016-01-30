## weewx-footer for weewx - Copyright 2013-2014 Hartmut Schweidler
## $Id: footer.inc 634 2014-09-08 08:34:04Z hes1 $
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
     weewx-Laufzeit:&nbsp; $station.uptime&nbsp;&nbsp;&#124;&nbsp;&nbsp;
     Serverlaufzeit:&nbsp; $station.os_uptime&nbsp;&nbsp;&#124;&nbsp;&nbsp;
     weewx  Version:&nbsp; $station.version&nbsp;&nbsp;&#124;&nbsp;&nbsp;
     Wetterstation:&nbsp; $station.hardware&nbsp;&nbsp;&#124;&nbsp;&nbsp;
     Zusatz: forecast; cmon; owfs und 13 one-wire-Sensoren
</div>

<p>
 #if $Extras.has_key('station_subtitle')
     $Extras.station_subtitle<br/>
 #end if
</p>
<hr />

<div class="navbar">
   <input type="button" value=" Test " onclick="openURL('ss/index.html')" />        
   <input type="button" value="   Aktuell   " onclick="openURL('index.html')" />
   <input type="button" value="  Vorschau   " onclick="openURL('forecast.html')" />
   <input type="button" value="    OWFS     " onclick="openURL('index2.html')" />
   <input type="button" value="     Tag     " onclick="openURL('day.html')" />
   <input type="button" value="    Woche    " onclick="openURL('week.html')" />
   <input type="button" value="    Monat    " onclick="openURL('month.html')" />
   <input type="button" value="    Jahr     " onclick="openURL('year.html')" />

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
                 <a href="http://blog.hes61.de/datenschutz/">&raquo; Datenschutz &laquo;</a></div>
</div>
<hr />
<p>
<iframe style="border: 0; height: 200px; width: 800px;" src="http://piwik.hes61.de/index.php?module=CoreAdminHome&amp;action=optOut&amp;language=de"></iframe> 
</p>

<!-- Piwik -->
<script type="text/javascript">
  var _paq = _paq || [];
  _paq.push(["trackPageView"]);
  _paq.push(["enableLinkTracking"]);

  (function() {
    var u=(("https:" == document.location.protocol) ? "https" : "http") + "://piwik.hes61.de/";
    _paq.push(["setTrackerUrl", u+"piwik.php"]);
    _paq.push(["setSiteId", "5"]);
    var d=document, g=d.createElement("script"), s=d.getElementsByTagName("script")[0]; g.type="text/javascript";
    g.defer=true; g.async=true; g.src=u+"piwik.js"; s.parentNode.insertBefore(g,s);
  })();
</script>
<noscript>
  <p><img src="http://piwik.hes61.de/piwik.php?idsite=5&amp;rec=1" style="border:0" alt="" /></p>
</noscript>
<!-- End Piwik Code -->

## Include the Google Analytics code if there is an ID available:
#if $Extras.has_key('googleAnalyticsId')
<script type="text/javascript">
  var gaJsHost = (("https:" == document.location.protocol) ? "https://ssl." : "http://www.");
  document.write(unescape("%3Cscript src='" + gaJsHost + "google-analytics.com/ga.js' type='text/javascript'%3E%3C/script%3E"));
</script>
<script type="text/javascript">
  try{
  var pageTracker = _gat._getTracker("$Extras.googleAnalyticsId");
  pageTracker._trackPageview();
  } catch(err) {}
</script>
#end if

</footer></div><!-- end id "footer" -->

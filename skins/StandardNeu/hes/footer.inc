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
     weewx-Laufzeit:&nbsp; $station.uptime&nbsp;&nbsp;&#124;&nbsp;&nbsp;
     Serverlaufzeit:&nbsp; $station.os_uptime&nbsp;&nbsp;&#124;&nbsp;&nbsp;
     weewx  Version:&nbsp; $station.version&nbsp;&nbsp;&#124;&nbsp;&nbsp;
     Wetterstation:&nbsp; $station.hardware&nbsp;&nbsp;&#124;&nbsp;&nbsp;
     Zusatz: forecast; cmon; owfs mit 13 one-wire-Sensoren
</div>

<p>
 #if $Extras.has_key('station_subtitle')
     $Extras.station_subtitle<br/>
 #end if
</p>
<hr />

<div class="navbar">
   <input type="button" value=" SteelGauge  " onclick="openURL('ss/index.html')" />        
   <input type="button" value="   Aktuell   " onclick="openURL('index.html')" />
   <input type="button" value="    OWFS     " onclick="openURL('index2.html')" />
   <input type="button" value="   Prognose  " onclick="openURL('forecastT.html')" />
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
                 <a href="http://v4v6.ipv6-test.com/api/myip.php"> IP ? </a> 
                 <a href="http://blog.hes61.de/datenschutz/">&raquo; Datenschutz &laquo;</a>

</div>
</div>
<hr />

<div align=center>

<!-- IPv6-test.com widget BEGIN -->
<script type="text/javascript">var _ipv6test_widget_style = {
border: "solid 1px #000",
font_size: "12px",
show_country_flags: true,
show_loading_anim: true,
ipv4_label_color: "#393",
ipv4_background_color: "#eee",
ipv6_label_color: "#339",
ipv6_background_color: "#ddd",
stats_position: "bottom",
stats_font_size: "10px",
stats_color: "#eee",
stats_color_v4: "#beb",
stats_color_v6: "#bbe",
stats_background_color: "#666"
}</script>
<div id="_ipv6test_widget" style="max-width:30em;display:none">loading <a href="http://ipv6-test.com/">IPv6 connection test</a> ...</div>
<script type="text/javascript" src="http://ipv6-test.com/api/widget.php?domain=referer" async="async"></script>
<!-- IPv6-test.com widget END -->
</div>


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

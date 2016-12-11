## forecast_Text.inc 1965 2016-03-27 19:26:24Z hes $

  <div class='legend'><h3>7 Tage Vorschau WeatherUnderground </h3>
    <table>
      <tr>
        <td><b>$forecast.xwuh(0).title</b><br />
        #set $hesicon = $forecast.xwuh(0).icon
        #if $hesicon == "skc" 
            #set $simg = 'forecast/images/' + $hesicon + '.jpg'
        #else
            #set $simg = 'forecast/images/' + $hesicon + $forecast.xwuh(0).pop + '.jpg'
        #end if
          <img src='$simg' alt='$forecast.xwuh(0).icon' /><br />$forecast.xwuh(0).iconT
        </td>
        <td><b>$forecast.xwuh(2).title</b><br />
        #set $hesicon = $forecast.xwuh(2).icon
        #if $hesicon == "skc"
            #set $simg = 'forecast/images/' + $hesicon + '.jpg'
        #else
            #set $simg = 'forecast/images/' + $hesicon + $forecast.xwuh(2).pop + '.jpg'
        #end if
          <img src='$simg' alt='$forecast.xwuh(2).icon' /><br />$forecast.xwuh(2).iconT
        </td>
        <td><b>$forecast.xwuh(4).title</b><br />
        #set $hesicon = $forecast.xwuh(4).icon
        #if $hesicon == "skc"
            #set $simg = 'forecast/images/' + $hesicon + '.jpg'
        #else
            #set $simg = 'forecast/images/' + $hesicon + $forecast.xwuh(4).pop + '.jpg'
        #end if
          <img src='$simg' alt='$forecast.xwuh(4).icon' /><br />$forecast.xwuh(4).iconT
        </td>
        <td><b>$forecast.xwuh(6).title</b><br />
        #set $hesicon = $forecast.xwuh(6).icon
        #if $hesicon == "skc"
            #set $simg = 'forecast/images/' + $hesicon + '.jpg'
        #else
            #set $simg = 'forecast/images/' + $hesicon + $forecast.xwuh(6).pop + '.jpg'
        #end if
          <img src='$simg' alt='$forecast.xwuh(6).icon' /><br />$forecast.xwuh(6).iconT
        </td>
        <td><b>$forecast.xwuh(8).title</b><br />
        #set $hesicon = $forecast.xwuh(8).icon
        #if $hesicon == "skc"
            #set $simg = 'forecast/images/' + $hesicon + '.jpg'
        #else
            #set $simg = 'forecast/images/' + $hesicon + $forecast.xwuh(8).pop + '.jpg'
        #end if
          <img src='$simg' alt='$forecast.xwuh(8).icon' /><br />$forecast.xwuh(8).iconT
        </td>
        <td><b>$forecast.xwuh(10).title</b><br />
        #set $hesicon = $forecast.xwuh(10).icon
        #if $hesicon == "skc"
            #set $simg = 'forecast/images/' + $hesicon + '.jpg'
        #else
            #set $simg = 'forecast/images/' + $hesicon + $forecast.xwuh(10).pop + '.jpg'
        #end if
          <img src='$simg' alt='$forecast.xwuh(10).icon' /><br />$forecast.xwuh(10).iconT
        </td>
        <td><b>$forecast.xwuh(12).title</b><br />
        #set $hesicon = $forecast.xwuh(12).icon
        #if $hesicon == "skc"
            #set $simg = 'forecast/images/' + $hesicon + '.jpg'
        #else
            #set $simg = 'forecast/images/' + $hesicon + $forecast.xwuh(12).pop + '.jpg'
        #end if
          <img src='$simg' alt='$forecast.xwuh(12).icon' /><br />$forecast.xwuh(12).iconT
        </td>
      </tr>
      <tr>
        <td><b>$forecast.xwuh(1).title</b><br />
        #set $hesicon = $forecast.xwuh(1).icon
        #if $hesicon == "nskc"
            #set $simg = 'forecast/images/' + $hesicon + '.jpg'
        #else
            #set $simg = 'forecast/images/' + $hesicon + $forecast.xwuh(1).pop + '.jpg'
        #end if
          <img src='$simg' alt='$forecast.xwuh(1).icon' /><br />$forecast.xwuh(1).iconT
        </td>
        <td><b>$forecast.xwuh(3).title</b><br />
        #set $hesicon = $forecast.xwuh(3).icon
        #if $hesicon == "nskc"
            #set $simg = 'forecast/images/' + $hesicon + '.jpg'
        #else
            #set $simg = 'forecast/images/' + $hesicon + $forecast.xwuh(3).pop + '.jpg'
        #end if
          <img src='$simg' alt='$forecast.xwuh(3).icon' /><br />$forecast.xwuh(3).iconT
        </td>
        <td><b>$forecast.xwuh(5).title</b><br />
        #set $hesicon = $forecast.xwuh(5).icon
        #if $hesicon == "nskc"
            #set $simg = 'forecast/images/' + $hesicon + '.jpg'
        #else
            #set $simg = 'forecast/images/' + $hesicon + $forecast.xwuh(5).pop + '.jpg'
        #end if
          <img src='$simg' alt='$forecast.xwuh(5).icon' /><br />$forecast.xwuh(5).iconT
        </td>
        <td><b>$forecast.xwuh(7).title</b><br />
        #set $hesicon = $forecast.xwuh(7).icon
        #if $hesicon == "nskc"
            #set $simg = 'forecast/images/' + $hesicon + '.jpg'
        #else
            #set $simg = 'forecast/images/' + $hesicon + $forecast.xwuh(7).pop + '.jpg'
        #end if
          <img src='$simg' alt='$forecast.xwuh(7).icon' /><br />$forecast.xwuh(7).iconT
        </td>
        <td><b>$forecast.xwuh(9).title</b><br />
        #set $hesicon = $forecast.xwuh(9).icon
        #if $hesicon == "nskc"
            #set $simg = 'forecast/images/' + $hesicon + '.jpg'
        #else
            #set $simg = 'forecast/images/' + $hesicon + $forecast.xwuh(9).pop + '.jpg'
        #end if
          <img src='$simg' alt='$forecast.xwuh(9).icon' /><br />$forecast.xwuh(9).iconT
        </td>
        <td><b>$forecast.xwuh(11).title</b><br />
        #set $hesicon = $forecast.xwuh(11).icon
        #if $hesicon == "nskc"
            #set $simg = 'forecast/images/' + $hesicon + '.jpg'
        #else
            #set $simg = 'forecast/images/' + $hesicon + $forecast.xwuh(11).pop + '.jpg'
        #end if
          <img src='$simg' alt='$forecast.xwuh(11).icon' /><br />$forecast.xwuh(11).iconT
        </td>
        <td><b>$forecast.xwuh(13).title</b><br />
        #set $hesicon = $forecast.xwuh(13).icon
        #if $hesicon == "nskc"
            #set $simg = 'forecast/images/' + $hesicon + '.jpg'
        #else
            #set $simg = 'forecast/images/' + $hesicon + $forecast.xwuh(13).pop + '.jpg'
        #end if
          <img src='$simg' alt='$forecast.xwuh(13).icon' /><br />$forecast.xwuh(13).iconT
        </td>
      </tr> 
    </table>
  </div>
<p>&nbsp;</p>
<table>
  #for $wuhs in $forecast.xwuhs
  <tr valign ="top" align="left">
   <td style="width: 20%;"><b>$wuhs.title</b><br />&nbsp;</td>
   <td style="width: 80%;">$wuhs.fcttext_metric</td>
  </tr>
  #end for
</table>
<p>Prognose von <a href="http://www.wunderground.com/cgi-bin/findweather/getForecast?query=pws:IMECKLEN20">WeatherUnderground</a></p>
<hr />


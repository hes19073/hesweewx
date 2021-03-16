#encoding UTF-8
<!-- about the station -->
#import platform
#import sys

#set $weePython = "Python %s" % (sys.version)
#set $weePlatform = "BS %s" % (platform.platform())

<div class="widget">
  <h3>Station</h3>
  <table class="about">
    <tr>
      <td class="label"><b>Weewx seit:</b></td>
      <td class="data">$year00</td>
    </tr>
    <tr>
      <td class="label">Hardware:</td>
      <td class="data">$station.hardware</td>
    </tr>
    <tr>
      <td class="label">Hardware:</td>
      <td class="data">Davis Station 6345 CSOV</td>
    </tr>
    <tr>
      <td class="label">Hardware:</td>
      <td class="data">Temp.-Sensor DS18B20</td>
    </tr>
    <tr>
      <td class="label">Hardware:</td>
      <td class="data">Geiger-Zähler GQ GMC-300E</td>
    </tr>
    <tr>
      <td class="label">Hardware:</td>
      <td class="data">Blitz-Sensor AS3935</td>
    </tr>
    <tr>
      <td class="label">Hardware:</td>
      <td class="data">Feinstaubsensor SDS011</td>
    </tr>
    <tr>
      <td class="label">Inbetriebnahme:</td>
      <td class="data">$start_time</td>
    </tr>
    <tr>
      <td class="label">Start DB:</td>
      <td class="data">$station.db_uptime</td>
    </tr>
    <tr>
      <td class="label">WeeWx uptime:</td>
      <td class="data">$station.uptime</td>
    </tr>
    <tr>
      <td class="label">Server uptime:</td>
      <td class="data">$station.os_uptime</td>
    </tr>
    <tr>
     <td class="label">Python:</td>
     <td class="label">$weePython</td>
    </tr>
    <tr>
      <td class="label">Plattform:</td>
      <td class="data">$weePlatform</td>
    </tr>
    <tr>
      <td class="label">WeeWx-Software:</td>
      <td class="data">$station.version</td>
    </tr>
   <tr><td colspan='2'>&nbsp;</td></tr>
    <tr>
      <td class="label"><b>Erweiterung</b></td>
      <td class="data"><i>Version</i></td>
    </tr>
    <tr>
      <td class="label">Berechnungen:</td>
      <td class="data">WD 3.0.1</td>
    </tr>
    <tr>
      <td class="label">Forecast:</td>
      <td class="data">3.4.0</td>
    </tr>
    <tr>
      <td class="label">ComputerMonitor:</td>
      <td class="data">0.16</td>
    </tr>
    <tr>
      <td class="label">OWFS version:</td>
      <td class="data">0.22</td>
    </tr>
    <tr>
      <td class="label">AS3935 Service:</td>
      <td class="data">0.6</td>
    </tr>
    <tr>
      <td class="label">Astro version:</td>
      <td class="data">WD Astro 2.0.0</td>
    </tr>
    <tr>
      <td class="label">windguru:</td>
      <td class="data">0.2</td>
    </tr>
    <tr>
      <td class="label">windfinder:</td>
      <td class="data">0.9</td>
    </tr>
    <tr>
      <td class="label">wetter:</td>
      <td class="data">0.6</td>
    </tr>
    <tr>
      <td class="label">wcloud:</td>
      <td class="data">0.13</td>
    </tr>
    <tr>
      <td class="label">snowhes:</td>
      <td class="data">0.2</td>
    </tr>
    <tr>
      <td class="label">DWD Pollen:</td>
      <td class="data">3.0.1</td>
    </tr>
    <tr>
      <td class="label">DWD Prognose:</td>
      <td class="data">3.0.5</td>
    </tr>
    <tr>
      <td class="label">Radioaktivität: </td>
      <td class="data">3.0.2</td>
    </tr>
    <tr>
      <td class="label">Cydia Pomonella:</td>
      <td class="data">3.0.2</td>
    </tr>
    <tr>
      <td class="label">Wachstumsgradtag:</td>
      <td class="data">3.0.2</td>
    </tr>
    <tr>
      <td class="label">Grünland Temperatur Summe:</td>
      <td class="data">3.0.2</td>
    </tr>
    <tr>
      <td class="label">Prognose AerisWeather:</td>
      <td class="data">3.0.1</td>
    </tr>
    <tr>
      <td class="label">Prognose DarkSky:</td>
      <td class="data">1.2.1</td>
    </tr>
    <tr>
      <td class="label">Wetterwarnung Aeris:</td>
      <td class="data">3.0.1</td>
    </tr>
    <tr>
      <td class="label">Wetterwarnung DWD:</td>
      <td class="data">3.0.1</td>
    </tr>
    <tr>
      <td class="label">Air Quality Aeris:</td>
      <td class="data">3.0.1</td>
    </tr>
    <tr>
      <td class="label">Grünland GTS:</td>
      <td class="data">0.4.1</td>
    </tr>
    <tr>
      <td class="label">Phenology:</td>
      <td class="data">1.2</td>
    </tr>
  </table>
</div>

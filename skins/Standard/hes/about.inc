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
      <td class="label">Hardware</td>
      <td class="data">$station.hardware</td>
    </tr>
    <tr>
      <td class="label">Hardware</td>
      <td class="data">6345 CSOV</td>
    </tr>
    <tr>
      <td class="label">Hardware</td>
      <td class="data">DS18B20</td>
    </tr>
    <tr>
      <td class="label">Hardware</td>
      <td class="data">GQ GMC-300E</td>
    </tr>
    <tr>
      <td class="label">Software</td>
      <td class="data">WeeWX $station.version</td>
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
     <td class="label">Python</td>
     <td class="label">$weePython</td>
    </tr>
    <tr>
      <td class="label">Platform</td>
      <td class="data">$weePlatform</td>
    </tr>
    <tr>
      <td class="label"><b>Erweiterung</b></td>
      <td class="data"><i>Version</i></td>
    </tr>
    <tr>
      <td class="label">Davis Forecast:</td>
      <td class="data">wd wsupp 1.2.0b1</td>
    </tr>
    <tr>
      <td class="label">Forecast:</td>
      <td class="data">3.2.14</td>
    </tr>
    <tr>
      <td class="label">ComputerMonitor</td>
      <td class="data">0.16</td>
    </tr>
    <tr>
      <td class="label">OWFS version:</td>
      <td class="data">0.20</td>
    </tr>
    <tr>
      <td class="label">Astro version:</td>
      <td class="data">wd 1.2.0b1</td>
    </tr>
    <tr>
      <td class="label">windguru:</td>
      <td class="data">0.1</td>
    </tr>
    <tr>
      <td class="label">windfinder:</td>
      <td class="data">0.8</td>
    </tr>
    <tr>
      <td class="label">wetter:</td>
      <td class="data">0.2</td>
    </tr>
    <tr>
      <td class="label">wcloud:</td>
      <td class="data">0.7</td>
    </tr>
    <tr>
      <td class="label">snowhes:</td>
      <td class="data">0.2</td>
    </tr>
    <tr>
      <td class="label">DWD Pollen</td>
      <td class="data">0.3</td>
    </tr>
    <tr>
      <td class="label">DWD Vorschau</td>
      <td class="data">0.5</td>
    </tr>
    <tr>
      <td class="label">Radioaktivität</td>
      <td class="data">0.2</td>
    </tr>
  </table>
</div>
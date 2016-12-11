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
      <td class="data">3.2.4</td>
    </tr>
    <tr>
      <td class="label">ComputerMonitor</td>
      <td class="data">0.14</td>
    </tr>
    <tr>
      <td class="label">OWFS version:</td>
      <td class="data">0.18</td>
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
  </table>
</div>

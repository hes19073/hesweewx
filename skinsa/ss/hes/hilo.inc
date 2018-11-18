## exfoliation for weewx - Copyright 2012-2013 Matthew Wall
## $Id: hilo.inc 619 2013-09-01 23:28:14Z mwall $

<!-- hi/lo readings in tabular form -->
<table class='metrics'>
  <tr>
    <td></td>
    <td class="metric_title">Heute</td>
    <td class="metric_title">Woche</td>
    <td class="metric_title">Monat</td>
    <td class="metric_title">Jahr</td>
    <td></td>
  </tr>

  <!-- outside -->

  <tr class="odd" style='vertical-align:top'>
    <td class="metric_name">Temperatur (max):</td>
    <td><span class="metric_value">$day.outTemp.max.formatted</span><br>
      <span class="hilo_time">$day.outTemp.maxtime</span></td>
    <td><span class="metric_value">$week.outTemp.max.formatted</span><br>
      <span class="hilo_time">$week.outTemp.maxtime.format("%d.%m.%Y")</span></td>
    <td><span class="metric_value">$month.outTemp.max.formatted</span><br>
      <span class="hilo_time">$month.outTemp.maxtime.format("%d.%m.%Y")</span></td>
    <td><span class="metric_value">$year.outTemp.max.formatted</span><br>
      <span class="hilo_time">$year.outTemp.maxtime.format("%d.%m.%Y")</span></td>
    <td class="metric_units">$unit.label.outTemp</td>
  </tr>
  <tr class="even" style='vertical-align:top'>
    <td class="metric_name">Temperatur (min):</td>
    <td><span class="metric_value">$day.outTemp.min.formatted</span><br>
      <span class="hilo_time">$day.outTemp.mintime</span></td>
    <td><span class="metric_value">$week.outTemp.min.formatted</span><br>
      <span class="hilo_time">$week.outTemp.mintime.format("%d.%m.%Y")</span></td>
    <td><span class="metric_value">$month.outTemp.min.formatted</span><br>
      <span class="hilo_time">$month.outTemp.mintime.format("%d.%m.%Y")</span></td>
    <td><span class="metric_value">$year.outTemp.min.formatted</span><br>
      <span class="hilo_time">$year.outTemp.mintime.format("%d.%m.%Y")</span></td>
    <td class="metric_units">$unit.label.outTemp</td>
  </tr>
  <tr class="odd" style='vertical-align:top'>
    <td class="metric_name">Luftfeuchte (max):</td>
    <td><span class="metric_value">$day.outHumidity.max.formatted</span><br>
      <span class="hilo_time">$day.outHumidity.maxtime</span></td>
    <td><span class="metric_value">$week.outHumidity.max.formatted</span><br>
      <span class="hilo_time">$week.outHumidity.maxtime.format("%d.%m.%Y")</span></td>
    <td><span class="metric_value">$month.outHumidity.max.formatted</span><br>
      <span class="hilo_time">$month.outHumidity.maxtime.format("%d.%m.%Y")</span></td>
    <td><span class="metric_value">$year.outHumidity.max.formatted</span><br>
      <span class="hilo_time">$year.outHumidity.maxtime.format("%d.%m.%Y")</span></td>
    <td class="metric_units">$unit.label.outHumidity</td>
  </tr>
  <tr class="even" style='vertical-align:top'>
    <td class="metric_name">Luftfeuchte (min):</td>
    <td><span class="metric_value">$day.outHumidity.min.formatted</span><br>
      <span class="hilo_time">$day.outHumidity.mintime</span></td>
    <td><span class="metric_value">$week.outHumidity.min.formatted</span><br>
      <span class="hilo_time">$week.outHumidity.mintime.format("%d.%m.%Y")</span></td>
    <td><span class="metric_value">$month.outHumidity.min.formatted</span><br>
      <span class="hilo_time">$month.outHumidity.mintime.format("%d.%m.%Y")</span></td>
    <td><span class="metric_value">$year.outHumidity.min.formatted</span><br>
      <span class="hilo_time">$year.outHumidity.mintime.format("%d.%m.%Y")</span></td>
    <td class="metric_units">$unit.label.outHumidity</td>
  </tr>
  <tr class="odd" style='vertical-align:top'>
    <td class="metric_name">Luftfeuchte 2 (max):</td>
    <td><span class="metric_value">$day.extraHumid1.max.formatted</span><br>
      <span class="hilo_time">$day.extraHumid1.maxtime</span></td>
    <td><span class="metric_value">$week.extraHumid1.max.formatted</span><br>
      <span class="hilo_time">$week.extraHumid1.maxtime.format("%d.%m.%Y")</span></td>
    <td><span class="metric_value">$month.extraHumid1.max.formatted</span><br>
      <span class="hilo_time">$month.extraHumid1.maxtime.format("%d.%m.%Y")</span></td>
    <td><span class="metric_value">$year.extraHumid1.max.formatted</span><br>
      <span class="hilo_time">$year.extraHumid1.maxtime.format("%d.%m.%Y")</span></td>
    <td class="metric_units">$unit.label.extraHumid1</td>
  </tr>
  <tr class="even" style='vertical-align:top'>
    <td class="metric_name">Luftfeuchte 2 (min):</td>
    <td><span class="metric_value">$day.extraHumid1.min.formatted</span><br>
      <span class="hilo_time">$day.extraHumid1.mintime</span></td>
    <td><span class="metric_value">$week.extraHumid1.min.formatted</span><br>
      <span class="hilo_time">$week.extraHumid1.mintime.format("%d.%m.%Y")</span></td>
    <td><span class="metric_value">$month.extraHumid1.min.formatted</span><br>
      <span class="hilo_time">$month.extraHumid1.mintime.format("%d.%m.%Y")</span></td>
    <td><span class="metric_value">$year.extraHumid1.min.formatted</span><br>
      <span class="hilo_time">$year.extraHumid1.mintime.format("%d.%m.%Y")</span></td>
    <td class="metric_units">$unit.label.extraHumid1</td>
  </tr> 
  <tr class="odd" style='vertical-align:top'>
    <td class="metric_name">Luftfeuchte 3 (max):</td>
    <td><span class="metric_value">$day.extraHumid2.max.formatted</span><br>
      <span class="hilo_time">$day.extraHumid2.maxtime</span></td>
    <td><span class="metric_value">$week.extraHumid2.max.formatted</span><br>
      <span class="hilo_time">$week.extraHumid2.maxtime.format("%d.%m.%Y")</span></td>
    <td><span class="metric_value">$month.extraHumid2.max.formatted</span><br>
      <span class="hilo_time">$month.extraHumid2.maxtime.format("%d.%m.%Y")</span></td>
    <td><span class="metric_value">$year.extraHumid2.max.formatted</span><br>
      <span class="hilo_time">$year.extraHumid2.maxtime.format("%d.%m.%Y")</span></td>
    <td class="metric_units">$unit.label.extraHumid2</td>
  </tr>
  <tr class="even" style='vertical-align:top'>
    <td class="metric_name">Luftfeuchte 3 (min):</td>
    <td><span class="metric_value">$day.extraHumid2.min.formatted</span><br>
      <span class="hilo_time">$day.extraHumid2.mintime</span></td>
    <td><span class="metric_value">$week.extraHumid2.min.formatted</span><br>
      <span class="hilo_time">$week.extraHumid2.mintime.format("%d.%m.%Y")</span></td>
    <td><span class="metric_value">$month.extraHumid2.min.formatted</span><br>
      <span class="hilo_time">$month.extraHumid2.mintime.format("%d.%m.%Y")</span></td>
    <td><span class="metric_value">$year.extraHumid2.min.formatted</span><br>
      <span class="hilo_time">$year.extraHumid2.mintime.format("%d.%m.%Y")</span></td>
    <td class="metric_units">$unit.label.extraHumid2</td>
  </tr>

  <tr class="odd" style='vertical-align:top'>
    <td class="metric_name">Taupunkt (max):</td>
    <td><span class="metric_value">$day.dewpoint.max.formatted</span><br>
      <span class="hilo_time">$day.dewpoint.maxtime</span></td>
    <td><span class="metric_value">$week.dewpoint.max.formatted</span><br>
      <span class="hilo_time">$week.dewpoint.maxtime.format("%d.%m.%Y")</span></td>
    <td><span class="metric_value">$month.dewpoint.max.formatted</span><br>
      <span class="hilo_time">$month.dewpoint.maxtime.format("%d.%m.%Y")</span></td>
    <td><span class="metric_value">$year.dewpoint.max.formatted</span><br>
      <span class="hilo_time">$year.dewpoint.maxtime.format("%d.%m.%Y")</span></td>
    <td class="metric_units">$unit.label.dewpoint</td>
  </tr>
  <tr class="even" style='vertical-align:top'>
    <td class="metric_name">Taupunkt (min):</td>
    <td><span class="metric_value">$day.dewpoint.min.formatted</span><br>
      <span class="hilo_time">$day.dewpoint.mintime</span></td>
    <td><span class="metric_value">$week.dewpoint.min.formatted</span><br>
      <span class="hilo_time">$week.dewpoint.mintime.format("%d.%m.%Y")</span></td>
    <td><span class="metric_value">$month.dewpoint.min.formatted</span><br>
      <span class="hilo_time">$month.dewpoint.mintime.format("%d.%m.%Y")</span></td>
    <td><span class="metric_value">$year.dewpoint.min.formatted</span><br>
      <span class="hilo_time">$year.dewpoint.mintime.format("%d.%m.%Y")</span></td>
    <td class="metric_units">$unit.label.dewpoint</td>
  </tr>
  <tr class="odd" style='vertical-align:top'>
    <td class="metric_name">Luftdruck (max):</td>
    <td><span class="metric_value">$day.barometer.max.formatted</span><br>
      <span class="hilo_time">$day.barometer.maxtime</span></td>
    <td><span class="metric_value">$week.barometer.max.formatted</span><br>
      <span class="hilo_time">$week.barometer.maxtime.format("%d.%m.%Y")</span></td>
    <td><span class="metric_value">$month.barometer.max.formatted</span><br>
      <span class="hilo_time">$month.barometer.maxtime.format("%d.%m.%Y")</span></td>
    <td><span class="metric_value">$year.barometer.max.formatted</span><br>
      <span class="hilo_time">$year.barometer.maxtime.format("%d.%m.%Y")</span></td>
    <td class="metric_units">$unit.label.barometer</td>
  </tr>
  <tr class="even" style='vertical-align:top'>
    <td class="metric_name">Luftdruck (min):</td>
    <td><span class="metric_value">$day.barometer.min.formatted</span><br>
      <span class="hilo_time">$day.barometer.mintime</span></td>
    <td><span class="metric_value">$week.barometer.min.formatted</span><br>
      <span class="hilo_time">$week.barometer.mintime.format("%d.%m.%Y")</span></td>
    <td><span class="metric_value">$month.barometer.min.formatted</span><br>
      <span class="hilo_time">$month.barometer.mintime.format("%d.%m.%Y")</span></td>
    <td><span class="metric_value">$year.barometer.min.formatted</span><br>
      <span class="hilo_time">$year.barometer.mintime.format("%d.%m.%Y")</span></td>
    <td class="metric_units">$unit.label.barometer</td>
  </tr>
  <tr class="odd" style='vertical-align:top'>
    <td class="metric_name">Hitzeindex (max):</td>
    <td><span class="metric_value">$day.heatindex.max.formatted</span><br>
      <span class="hilo_time">$day.heatindex.maxtime</span></td>
    <td><span class="metric_value">$week.heatindex.max.formatted</span><br>
      <span class="hilo_time">$week.heatindex.maxtime.format("%d.%m.%Y")</span></td>
    <td><span class="metric_value">$month.heatindex.max.formatted</span><br>
      <span class="hilo_time">$month.heatindex.maxtime.format("%d.%m.%Y")</span></td>
    <td><span class="metric_value">$year.heatindex.max.formatted</span><br>
      <span class="hilo_time">$year.heatindex.maxtime.format("%d.%m.%Y")</span></td>
    <td class="metric_units">$unit.label.heatindex</td>
  </tr>
  <tr class="even" style='vertical-align:top'>
    <td class="metric_name">Windchill (min):</td>
    <td><span class="metric_value">$day.windchill.min.formatted</span><br>
      <span class="hilo_time">$day.windchill.mintime</span></td>
    <td><span class="metric_value">$week.windchill.min.formatted</span><br>
      <span class="hilo_time">$week.windchill.mintime.format("%d.%m.%Y")</span></td>
    <td><span class="metric_value">$month.windchill.min.formatted</span><br>
      <span class="hilo_time">$month.windchill.mintime.format("%d.%m.%Y")</span></td>
    <td><span class="metric_value">$year.windchill.min.formatted</span><br>
      <span class="hilo_time">$year.windchill.mintime.format("%d.%m.%Y")</span></td>
    <td class="metric_units">$unit.label.windchill</td>
  </tr>
  <tr class="odd" style='vertical-align:top'>
    <td class="metric_name">Windgeschwindigkeit (max):</td>
    <td><span class="metric_value">$day.wind.max.formatted</span><br>
      <span class="hilo_time">$day.wind.maxtime</span></td>
    <td><span class="metric_value">$week.wind.max.formatted</span><br>
      <span class="hilo_time">$week.wind.maxtime.format("%d.%m.%Y")</span></td>
    <td><span class="metric_value">$month.wind.max.formatted</span><br>
      <span class="hilo_time">$month.wind.maxtime.format("%d.%m.%Y")</span></td>
    <td><span class="metric_value">$year.wind.max.formatted</span><br>
      <span class="hilo_time">$year.wind.maxtime.format("%d.%m.%Y")</span></td>
    <td class="metric_units">$unit.label.wind</td>
  </tr>
  <tr class="even" style='vertical-align:top'>
    <td class="metric_name">&Oslash; Windgeschwindigkeit:</td>
    <td><span class="metric_value">$day.wind.avg.formatted</span><br>
      <span class="hilo_time">&nbsp;</span></td>
    <td><span class="metric_value">$week.wind.avg.formatted</span></td>
    <td><span class="metric_value">$month.wind.avg.formatted</span></td>
    <td><span class="metric_value">$year.wind.avg.formatted</span></td>
    <td class="metric_units">$unit.label.wind</td>
  </tr>
  <tr class="odd" style='vertical-align:top'>
    <td class="metric_name">Regenschauer (max):</td>
    <td><span class="metric_value">$day.rainRate.max.formatted</span><br>
      <span class="hilo_time">$day.rainRate.maxtime</span></td>
    <td><span class="metric_value">$week.rainRate.max.formatted</span><br>
      <span class="hilo_time">$week.rainRate.maxtime.format("%d.%m.%Y")</span></td>
    <td><span class="metric_value">$month.rainRate.max.formatted</span><br>
      <span class="hilo_time">$month.rainRate.maxtime.format("%d.%m.%Y")</span></td>
    <td><span class="metric_value">$year.rainRate.max.formatted</span><br>
      <span class="hilo_time">$year.rainRate.maxtime.format("%d.%m.%Y")</span></td>
    <td class="metric_units">$unit.label.rainRate</td>
  </tr>
  <tr class="even" style='vertical-align:top'>
    <td class="metric_name">Regen gesamt:<br />&nbsp;</td>
    <td><span class="metric_value">$day.rain.sum.formatted</span><br>
    <span class="hilo_time"> </span></td>
    <td><span class="metric_value">$week.rain.sum.formatted</span></td>
    <td><span class="metric_value">$month.rain.sum.formatted</span></td>
    <td><span class="metric_value">$year.rain.sum.formatted</span></td>
    <td class="metric_units">$unit.label.rain</td>
  </tr>

  <tr><td colspan="6">&nbsp;Wassertemperatur Sensor DS18B20<br />&nbsp;</td></tr>
  <tr class="odd" style='vertical-align:top'>
    <td class="metric_name">Teich (max):</td>
    <td><span class="metric_value">$day.extraTemp1.max.formatted</span><br>
      <span class="hilo_time">$day.extraTemp1.maxtime</span></td>
    <td><span class="metric_value">$week.extraTemp1.max.formatted</span><br>
      <span class="hilo_time">$week.extraTemp1.maxtime.format("%d.%m.%Y")</span></td>
    <td><span class="metric_value">$month.extraTemp1.max.formatted</span><br>
      <span class="hilo_time">$month.extraTemp1.maxtime.format("%d.%m.%Y")</span></td>
    <td><span class="metric_value">$year.extraTemp1.max.formatted</span><br>
      <span class="hilo_time">$year.extraTemp1.maxtime.format("%d.%m.%Y")</span></td>
    <td class="metric_units">$unit.label.extraTemp1</td>
  </tr>
  <tr class="even" style='vertical-align:top'>
    <td class="metric_name">Teich (min):</td>
    <td><span class="metric_value">$day.extraTemp1.min.formatted</span><br>
      <span class="hilo_time">$day.extraTemp1.mintime</span></td>
    <td><span class="metric_value">$week.extraTemp1.min.formatted</span><br>
      <span class="hilo_time">$week.extraTemp1.mintime.format("%d.%m.%Y")</span></td>
    <td><span class="metric_value">$month.extraTemp1.min.formatted</span><br>
      <span class="hilo_time">$month.extraTemp1.mintime.format("%d.%m.%Y")</span></td>
    <td><span class="metric_value">$year.extraTemp1.min.formatted</span><br>
      <span class="hilo_time">$year.extraTemp1.mintime.format("%d.%m.%Y")</span></td>
    <td class="metric_units">$unit.label.extraTemp1</td>
  </tr>

  <tr class="odd" style='vertical-align:top'>
    <td class="metric_name">Schwimmteich (max):</td>
    <td><span class="metric_value">$day.extraTemp2.max.formatted</span><br>
      <span class="hilo_time">$day.extraTemp2.maxtime</span></td>
    <td><span class="metric_value">$week.extraTemp2.max.formatted</span><br>
      <span class="hilo_time">$week.extraTemp2.maxtime.format("%d.%m.%Y")</span></td>
    <td><span class="metric_value">$month.extraTemp2.max.formatted</span><br>
      <span class="hilo_time">$month.extraTemp2.maxtime.format("%d.%m.%Y")</span></td>
    <td><span class="metric_value">$year.extraTemp2.max.formatted</span><br>
      <span class="hilo_time">$year.extraTemp2.maxtime.format("%d.%m.%Y")</span></td>
    <td class="metric_units">$unit.label.extraTemp2</td>
  </tr>
  <tr class="even" style='vertical-align:top'>
    <td class="metric_name">Schwimmteich (min):</td>
    <td><span class="metric_value">$day.extraTemp2.min.formatted</span><br>
      <span class="hilo_time">$day.extraTemp2.mintime</span></td>
    <td><span class="metric_value">$week.extraTemp2.min.formatted</span><br>
      <span class="hilo_time">$week.extraTemp2.mintime.format("%d.%m.%Y")</span></td>
    <td><span class="metric_value">$month.extraTemp2.min.formatted</span><br>
      <span class="hilo_time">$month.extraTemp2.mintime.format("%d.%m.%Y")</span></td>
    <td><span class="metric_value">$year.extraTemp2.min.formatted</span><br>
      <span class="hilo_time">$year.extraTemp2.mintime.format("%d.%m.%Y")</span></td>
    <td class="metric_units">$unit.label.extraTemp2</td>
  </tr>

  <tr class="odd" style='vertical-align:top'>
    <td class="metric_name">Schwimmteich Grund (max):</td>
    <td><span class="metric_value">$day.extraTemp3.max.formatted</span><br>
      <span class="hilo_time">$day.extraTemp3.maxtime</span></td>
    <td><span class="metric_value">$week.extraTemp3.max.formatted</span><br>
      <span class="hilo_time">$week.extraTemp3.maxtime.format("%d.%m.%Y")</span></td>
    <td><span class="metric_value">$month.extraTemp3.max.formatted</span><br>
      <span class="hilo_time">$month.extraTemp3.maxtime.format("%d.%m.%Y")</span></td>
    <td><span class="metric_value">$year.extraTemp3.max.formatted</span><br>
      <span class="hilo_time">$year.extraTemp3.maxtime.format("%d.%m.%Y")</span></td>
    <td class="metric_units">$unit.label.extraTemp3</td>
  </tr>
  <tr class="even" style='vertical-align:top'>
    <td class="metric_name">Schwimmteich Grund (min):</td>
    <td><span class="metric_value">$day.extraTemp3.min.formatted</span><br>
      <span class="hilo_time">$day.extraTemp3.mintime</span></td>
    <td><span class="metric_value">$week.extraTemp3.min.formatted</span><br>
      <span class="hilo_time">$week.extraTemp3.mintime.format("%d.%m.%Y")</span></td>
    <td><span class="metric_value">$month.extraTemp3.min.formatted</span><br>
      <span class="hilo_time">$month.extraTemp3.mintime.format("%d.%m.%Y")</span></td>
    <td><span class="metric_value">$year.extraTemp3.min.formatted</span><br>
      <span class="hilo_time">$year.extraTemp3.mintime.format("%d.%m.%Y")</span></td>
    <td class="metric_units">$unit.label.extraTemp3</td>
  </tr>

  <tr class="odd" style='vertical-align:top'>
    <td class="metric_name">Gartenteich (max):</td>
    <td><span class="metric_value">$day.extraTemp6.max.formatted</span><br>
      <span class="hilo_time">$day.extraTemp6.maxtime</span></td>
    <td><span class="metric_value">$week.extraTemp6.max.formatted</span><br>
      <span class="hilo_time">$week.extraTemp6.maxtime.format("%d.%m.%Y")</span></td>
    <td><span class="metric_value">$month.extraTemp6.max.formatted</span><br>
      <span class="hilo_time">$month.extraTemp6.maxtime.format("%d.%m.%Y")</span></td>
    <td><span class="metric_value">$year.extraTemp6.max.formatted</span><br>
      <span class="hilo_time">$year.extraTemp6.maxtime.format("%d.%m.%Y")</span></td>
    <td class="metric_units">$unit.label.extraTemp6</td>
  </tr>
  <tr class="even" style='vertical-align:top'>
    <td class="metric_name">Gartenteich (min):</td>
    <td><span class="metric_value">$day.extraTemp6.min.formatted</span><br>
      <span class="hilo_time">$day.extraTemp6.mintime</span></td>
    <td><span class="metric_value">$week.extraTemp6.min.formatted</span><br>
      <span class="hilo_time">$week.extraTemp6.mintime.format("%d.%m.%Y")</span></td>
    <td><span class="metric_value">$month.extraTemp6.min.formatted</span><br>
      <span class="hilo_time">$month.extraTemp6.mintime.format("%d.%m.%Y")</span></td>
    <td><span class="metric_value">$year.extraTemp6.min.formatted</span><br>
      <span class="hilo_time">$year.extraTemp6.mintime.format("%d.%m.%Y")</span></td>
    <td class="metric_units">$unit.label.extraTemp6</td>
  </tr>

  <tr><td colspan="6">&nbsp;Temperatur  Sensor DS18B20<br />&nbsp;</td></tr>
  <tr class="odd" style='vertical-align:top'>
    <td class="metric_name">Boden +200 cm (max):</td>
    <td><span class="metric_value">$day.extraTemp4.max.formatted</span><br>
      <span class="hilo_time">$day.extraTemp4.maxtime</span></td>
    <td><span class="metric_value">$week.extraTemp4.max.formatted</span><br>
      <span class="hilo_time">$week.extraTemp4.maxtime.format("%d.%m.%Y")</span></td>
    <td><span class="metric_value">$month.extraTemp4.max.formatted</span><br>
      <span class="hilo_time">$month.extraTemp4.maxtime.format("%d.%m.%Y")</span></td>
    <td><span class="metric_value">$year.extraTemp4.max.formatted</span><br>
      <span class="hilo_time">$year.extraTemp4.maxtime.format("%d.%m.%Y")</span></td>
    <td class="metric_units">$unit.label.inTemp</td>
  </tr>
  <tr class="even" style='vertical-align:top'>
    <td class="metric_name">Boden +200 cm (min):</td>
    <td><span class="metric_value">$day.extraTemp4.min.formatted</span><br>
      <span class="hilo_time">$day.extraTemp4.mintime</span></td>
    <td><span class="metric_value">$week.extraTemp4.min.formatted</span><br>
      <span class="hilo_time">$week.extraTemp4.mintime.format("%d.%m.%Y")</span></td>
    <td><span class="metric_value">$month.extraTemp4.min.formatted</span><br>
      <span class="hilo_time">$month.extraTemp4.mintime.format("%d.%m.%Y")</span></td>
    <td><span class="metric_value">$year.extraTemp4.min.formatted</span><br>
      <span class="hilo_time">$year.extraTemp4.mintime.format("%d.%m.%Y")</span></td>
    <td class="metric_units">$unit.label.inTemp</td>
  </tr>
  <tr class="odd" style='vertical-align:top'>
    <td class="metric_name">Boden +100 cm (max):</td>
    <td><span class="metric_value">$day.extraTemp7.max.formatted</span><br>
      <span class="hilo_time">$day.extraTemp7.maxtime</span></td>
    <td><span class="metric_value">$week.extraTemp7.max.formatted</span><br>
      <span class="hilo_time">$week.extraTemp7.maxtime.format("%d.%m.%Y")</span></td>
    <td><span class="metric_value">$month.extraTemp7.max.formatted</span><br>
      <span class="hilo_time">$month.extraTemp7.maxtime.format("%d.%m.%Y")</span></td>
    <td><span class="metric_value">$year.extraTemp7.max.formatted</span><br>
      <span class="hilo_time">$year.extraTemp7.maxtime.format("%d.%m.%Y")</span></td>
    <td class="metric_units">$unit.label.inTemp</td>
  </tr>
  <tr class="even" style='vertical-align:top'>
    <td class="metric_name">Boden +100 cm (min):</td>
    <td><span class="metric_value">$day.extraTemp7.min.formatted</span><br>
      <span class="hilo_time">$day.extraTemp7.mintime</span></td>
    <td><span class="metric_value">$week.extraTemp7.min.formatted</span><br>
      <span class="hilo_time">$week.extraTemp7.mintime.format("%d.%m.%Y")</span></td>
    <td><span class="metric_value">$month.extraTemp7.min.formatted</span><br>
      <span class="hilo_time">$month.extraTemp7.mintime.format("%d.%m.%Y")</span></td>
    <td><span class="metric_value">$year.extraTemp7.min.formatted</span><br>
      <span class="hilo_time">$year.extraTemp7.mintime.format("%d.%m.%Y")</span></td>
    <td class="metric_units">$unit.label.inTemp</td>
  </tr>
  <tr class="odd" style='vertical-align:top'>
    <td class="metric_name">Boden +5 cm (max):</td>
    <td><span class="metric_value">$day.extraTemp5.max.formatted</span><br>
      <span class="hilo_time">$day.extraTemp5.maxtime</span></td>
    <td><span class="metric_value">$week.extraTemp5.max.formatted</span><br>
      <span class="hilo_time">$week.extraTemp5.maxtime.format("%d.%m.%Y")</span></td>
    <td><span class="metric_value">$month.extraTemp5.max.formatted</span><br>
      <span class="hilo_time">$month.extraTemp5.maxtime.format("%d.%m.%Y")</span></td>
    <td><span class="metric_value">$year.extraTemp5.max.formatted</span><br>
      <span class="hilo_time">$year.extraTemp5.maxtime.format("%d.%m.%Y")</span></td>
    <td class="metric_units">$unit.label.inTemp</td>
  </tr>
  <tr class="even" style='vertical-align:top'>
    <td class="metric_name">Boden +5 cm (min):</td>
    <td><span class="metric_value">$day.extraTemp5.min.formatted</span><br>
      <span class="hilo_time">$day.extraTemp5.mintime</span></td>
    <td><span class="metric_value">$week.extraTemp5.min.formatted</span><br>
      <span class="hilo_time">$week.extraTemp5.mintime.format("%d.%m.%Y")</span></td>
    <td><span class="metric_value">$month.extraTemp5.min.formatted</span><br>
      <span class="hilo_time">$month.extraTemp5.mintime.format("%d.%m.%Y")</span></td>
    <td><span class="metric_value">$year.extraTemp5.min.formatted</span><br>
      <span class="hilo_time">$year.extraTemp5.mintime.format("%d.%m.%Y")</span></td>
    <td class="metric_units">$unit.label.inTemp</td>
  </tr>

  <tr class="odd" style='vertical-align:top'>
    <td class="metric_name">Boden -5 cm (max):</td>
    <td><span class="metric_value">$day.soilTemp1.max.formatted</span><br>
      <span class="hilo_time">$day.soilTemp1.maxtime</span></td>
    <td><span class="metric_value">$week.soilTemp1.max.formatted</span><br>
      <span class="hilo_time">$week.soilTemp1.maxtime.format("%d.%m.%Y")</span></td>
    <td><span class="metric_value">$month.soilTemp1.max.formatted</span><br>
      <span class="hilo_time">$month.soilTemp1.maxtime.format("%d.%m.%Y")</span></td>
    <td><span class="metric_value">$year.soilTemp1.max.formatted</span><br>
      <span class="hilo_time">$year.soilTemp1.maxtime.format("%d.%m.%Y")</span></td>
    <td class="metric_units">$unit.label.soilTemp1</td>
  </tr>
  <tr class="even" style='vertical-align:top'>
    <td class="metric_name">Boden -5 cm (min):</td>
    <td><span class="metric_value">$day.soilTemp1.min.formatted</span><br>
      <span class="hilo_time">$day.soilTemp1.mintime</span></td>
    <td><span class="metric_value">$week.soilTemp1.min.formatted</span><br>
      <span class="hilo_time">$week.soilTemp1.mintime.format("%d.%m.%Y")</span></td>
    <td><span class="metric_value">$month.soilTemp1.min.formatted</span><br>
      <span class="hilo_time">$month.soilTemp1.mintime.format("%d.%m.%Y")</span></td>
    <td><span class="metric_value">$year.soilTemp1.min.formatted</span><br>
      <span class="hilo_time">$year.soilTemp1.mintime.format("%d.%m.%Y")</span></td>
    <td class="metric_units">$unit.label.soilTemp1</td>
  </tr>

  <tr class="odd" style='vertical-align:top'>
    <td class="metric_name">Boden -10 cm (max):</td>
    <td><span class="metric_value">$day.soilTemp2.max.formatted</span><br>
      <span class="hilo_time">$day.soilTemp2.maxtime</span></td>
    <td><span class="metric_value">$week.soilTemp2.max.formatted</span><br>
      <span class="hilo_time">$week.soilTemp2.maxtime.format("%d.%m.%Y")</span></td>
    <td><span class="metric_value">$month.soilTemp2.max.formatted</span><br>
      <span class="hilo_time">$month.soilTemp2.maxtime.format("%d.%m.%Y")</span></td>
    <td><span class="metric_value">$year.soilTemp2.max.formatted</span><br>
      <span class="hilo_time">$year.soilTemp2.maxtime.format("%d.%m.%Y")</span></td>
    <td class="metric_units">$unit.label.soilTemp2</td>
  </tr>
  <tr class="even" style='vertical-align:top'>
    <td class="metric_name">Boden -10 cm (min):</td>
    <td><span class="metric_value">$day.soilTemp2.min.formatted</span><br>
      <span class="hilo_time">$day.soilTemp2.mintime</span></td>
    <td><span class="metric_value">$week.soilTemp2.min.formatted</span><br>
      <span class="hilo_time">$week.soilTemp2.mintime.format("%d.%m.%Y")</span></td>
    <td><span class="metric_value">$month.soilTemp2.min.formatted</span><br>
      <span class="hilo_time">$month.soilTemp2.mintime.format("%d.%m.%Y")</span></td>
    <td><span class="metric_value">$year.soilTemp2.min.formatted</span><br>
      <span class="hilo_time">$year.soilTemp2.mintime.format("%d.%m.%Y")</span></td>
    <td class="metric_units">$unit.label.soilTemp2</td>
  </tr>

  <tr class="odd" style='vertical-align:top'>
    <td class="metric_name">Boden -20 cm (max):</td>
    <td><span class="metric_value">$day.soilTemp3.max.formatted</span><br>
      <span class="hilo_time">$day.soilTemp3.maxtime</span></td>
    <td><span class="metric_value">$week.soilTemp3.max.formatted</span><br>
      <span class="hilo_time">$week.soilTemp3.maxtime.format("%d.%m.%Y")</span></td>
    <td><span class="metric_value">$month.soilTemp3.max.formatted</span><br>
      <span class="hilo_time">$month.soilTemp3.maxtime.format("%d.%m.%Y")</span></td>
    <td><span class="metric_value">$year.soilTemp3.max.formatted</span><br>
      <span class="hilo_time">$year.soilTemp3.maxtime.format("%d.%m.%Y")</span></td>
    <td class="metric_units">$unit.label.soilTemp3</td>
  </tr>
  <tr class="even" style='vertical-align:top'>
    <td class="metric_name">Boden -20 cm (min):</td>
    <td><span class="metric_value">$day.soilTemp3.min.formatted</span><br>
      <span class="hilo_time">$day.soilTemp3.mintime</span></td>
    <td><span class="metric_value">$week.soilTemp3.min.formatted</span><br>
      <span class="hilo_time">$week.soilTemp3.mintime.format("%d.%m.%Y")</span></td>
    <td><span class="metric_value">$month.soilTemp3.min.formatted</span><br>
      <span class="hilo_time">$month.soilTemp3.mintime.format("%d.%m.%Y")</span></td>
    <td><span class="metric_value">$year.soilTemp3.min.formatted</span><br>
      <span class="hilo_time">$year.soilTemp3.mintime.format("%d.%m.%Y")</span></td>
    <td class="metric_units">$unit.label.soilTemp3</td>
  </tr>

  <tr class="odd" style='vertical-align:top'>
    <td class="metric_name">Boden -50 cm (max):</td>
    <td><span class="metric_value">$day.soilTemp4.max.formatted</span><br>
      <span class="hilo_time">$day.soilTemp4.maxtime</span></td>
    <td><span class="metric_value">$week.soilTemp4.max.formatted</span><br>
      <span class="hilo_time">$week.soilTemp4.maxtime.format("%d.%m.%Y")</span></td>
    <td><span class="metric_value">$month.soilTemp4.max.formatted</span><br>
      <span class="hilo_time">$month.soilTemp4.maxtime.format("%d.%m.%Y")</span></td>
    <td><span class="metric_value">$year.soilTemp4.max.formatted</span><br>
      <span class="hilo_time">$year.soilTemp4.maxtime.format("%d.%m.%Y")</span></td>
    <td class="metric_units">$unit.label.soilTemp4</td>
  </tr>
  <tr class="even" style='vertical-align:top'>
    <td class="metric_name">Boden -50 cm (min):</td>
    <td><span class="metric_value">$day.soilTemp4.min.formatted</span><br>
      <span class="hilo_time">$day.soilTemp4.mintime</span></td>
    <td><span class="metric_value">$week.soilTemp4.min.formatted</span><br>
      <span class="hilo_time">$week.soilTemp4.mintime.format("%d.%m.%Y")</span></td>
    <td><span class="metric_value">$month.soilTemp4.min.formatted</span><br>
      <span class="hilo_time">$month.soilTemp4.mintime.format("%d.%m.%Y")</span></td>
    <td><span class="metric_value">$year.soilTemp4.min.formatted</span><br>
      <span class="hilo_time">$year.soilTemp4.mintime.format("%d.%m.%Y")</span></td>
    <td class="metric_units">$unit.label.soilTemp4</td>
  </tr>

  <tr class="odd" style='vertical-align:top'>
    <td class="metric_name">Boden -100 cm (max):</td>
    <td><span class="metric_value">$day.soilTemp5.max.formatted</span><br>
      <span class="hilo_time">$day.soilTemp5.maxtime</span></td>
    <td><span class="metric_value">$week.soilTemp5.max.formatted</span><br>
      <span class="hilo_time">$week.soilTemp5.maxtime.format("%d.%m.%Y")</span></td>
    <td><span class="metric_value">$month.soilTemp5.max.formatted</span><br>
      <span class="hilo_time">$month.soilTemp5.maxtime.format("%d.%m.%Y")</span></td>
    <td><span class="metric_value">$year.soilTemp5.max.formatted</span><br>
      <span class="hilo_time">$year.soilTemp5.maxtime.format("%d.%m.%Y")</span></td>
    <td class="metric_units">$unit.label.soilTemp5</td>
  </tr>
  <tr class="even" style='vertical-align:top'>
    <td class="metric_name">Boden -100 cm (min):</td>
    <td><span class="metric_value">$day.soilTemp5.min.formatted</span><br>
      <span class="hilo_time">$day.soilTemp5.mintime</span></td>
    <td><span class="metric_value">$week.soilTemp5.min.formatted</span><br>
      <span class="hilo_time">$week.soilTemp5.mintime.format("%d.%m.%Y")</span></td>
    <td><span class="metric_value">$month.soilTemp5.min.formatted</span><br>
      <span class="hilo_time">$month.soilTemp5.mintime.format("%d.%m.%Y")</span></td>
    <td><span class="metric_value">$year.soilTemp5.min.formatted</span><br>
      <span class="hilo_time">$year.soilTemp5.mintime.format("%d.%m.%Y")</span></td>
    <td class="metric_units">$unit.label.soilTemp5</td>
  </tr>




  <!-- inside -->

  <tr><td colspan="6">&nbsp;Innen&nbsp;<br></td></tr>
  <tr class="odd" style='vertical-align:top'>
    <td class="metric_name">Temperatur (max):</td>
    <td><span class="metric_value">$day.inTemp.max.formatted</span><br>
      <span class="hilo_time">$day.inTemp.maxtime</span></td>
    <td><span class="metric_value">$week.inTemp.max.formatted</span><br>
      <span class="hilo_time">$week.inTemp.maxtime.format("%d.%m.%Y")</span></td>
    <td><span class="metric_value">$month.inTemp.max.formatted</span><br>
      <span class="hilo_time">$month.inTemp.maxtime.format("%d.%m.%Y")</span></td>
    <td><span class="metric_value">$year.inTemp.max.formatted</span><br>
      <span class="hilo_time">$year.inTemp.maxtime.format("%d.%m.%Y")</span></td>
    <td class="metric_units">$unit.label.inTemp</td>
  </tr>
  <tr class="even" style='vertical-align:top'>
    <td class="metric_name">Temperatur (min):</td>
    <td><span class="metric_value">$day.inTemp.min.formatted</span><br>
      <span class="hilo_time">$day.inTemp.mintime</span></td>
    <td><span class="metric_value">$week.inTemp.min.formatted</span><br>
      <span class="hilo_time">$week.inTemp.mintime.format("%d.%m.%Y")</span></td>
    <td><span class="metric_value">$month.inTemp.min.formatted</span><br>
      <span class="hilo_time">$month.inTemp.mintime.format("%d.%m.%Y")</span></td>
    <td><span class="metric_value">$year.inTemp.min.formatted</span><br>
      <span class="hilo_time">$year.inTemp.mintime.format("%d.%m.%Y")</span></td>
    <td class="metric_units">$unit.label.inTemp</td>
  </tr>
  <tr class="odd" style='vertical-align:top'>
    <td class="metric_name">Luftfeuchte (max):</td>
    <td><span class="metric_value">$day.inHumidity.max.formatted</span><br>
      <span class="hilo_time">$day.inHumidity.maxtime</span></td>
    <td><span class="metric_value">$week.inHumidity.max.formatted</span><br>
      <span class="hilo_time">$week.inHumidity.maxtime.format("%d.%m.%Y")</span></td>
    <td><span class="metric_value">$month.inHumidity.max.formatted</span><br>
      <span class="hilo_time">$month.inHumidity.maxtime.format("%d.%m.%Y")</span></td>
    <td><span class="metric_value">$year.inHumidity.max.formatted</span><br>
      <span class="hilo_time">$year.inHumidity.maxtime.format("%d.%m.%Y")</span></td>
    <td class="metric_units">$unit.label.inHumidity</td>
  </tr>
  <tr class="even" style='vertical-align:top'>
    <td class="metric_name">Luftfeuchte (min):</td>
    <td><span class="metric_value">$day.inHumidity.min.formatted</span><br>
      <span class="hilo_time">$day.inHumidity.mintime</span></td>
    <td><span class="metric_value">$week.inHumidity.min.formatted</span><br>
      <span class="hilo_time">$week.inHumidity.mintime.format("%d.%m.%Y")</span></td>
    <td><span class="metric_value">$month.inHumidity.min.formatted</span><br>
      <span class="hilo_time">$month.inHumidity.mintime.format("%d.%m.%Y")</span></td>
    <td><span class="metric_value">$year.inHumidity.min.formatted</span><br>
      <span class="hilo_time">$year.inHumidity.mintime.format("%d.%m.%Y")</span></td>
    <td class="metric_units">$unit.label.inHumidity</td>
  </tr>

</table>

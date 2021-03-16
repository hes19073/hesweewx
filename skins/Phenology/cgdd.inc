## ==================================================boilerplate»=====
## Phenology Report Template
## 
## This script is distributed as part of the Phenology Extension to
## WeeWX.  WeeWX is maintained by Tom Keffer and Matthew Wall.  This
## script is maintained by Chuck Rhode although it may contain
## portions copied from Keffer and Wall or directly inspired by them.
## 
## Copyright 2018—2021 by Chuck Rhode.
## 
## See LICENSE.txt for your rights.
## 
## =================================================«boilerplate======
#errorCatcher Echo
#encoding UTF-8
#import weeutil.weeutil
#import weewx.units
#import weewx.xtypes
#import user.phenology
#set $phenologies = user.phenology.Phenologies().load_from_extras($Extras)
#set $themes = user.phenology.expand_themes($Extras.Themes)
#set $date_format = "%d %b"
#set $now_format = "%d.%m.%Y"
#set $db_manager = $latest.db_lookup()
#set $converter = $generator.converter

#for $model in $phenologies.values()

## $model attributes are:
## 
##   ref
##   name_scientific
##   name_common
##   threshold
##   cutoff
##   method
##   start_date
##   biofix_is_required
##   biofix
##   stages
##
    <div id="title_bar">
      <div id="title">
        #if $model.name_scientific == $model.name_common
      <h1>$model.name_scientific</h1>
      <h3>$model.name_de</h3>
	#else
      <h1>$model.name_scientific ($model.name_common)</h1>
      <h3>$model.name_de</h3>
	#end if name_scientific == name_common    
      </div>
    </div>
    <div id="contents">
      <img src="${model.name_common}.png" alt="$model.name_common" />
      <table>
	#set $latest_ts = user.phenology.get_generation_ts(None, $Extras, $db_manager)
	#set $earliest_ts = $latest_ts - 2419200  ## 28 days
	#set $run_date_t = weewx.units.ValueTuple($latest_ts, 'unix_epoch', 'group_time')
	#set $run_date_h = weewx.units.ValueHelper($run_date_t, converter=$converter)
	#set $t = $model.threshold[0]
	#set $u = $model.threshold[1]
	#if $t in ['None', 'none']
            #set $threshold_t = weewx.units.ValueTuple(None, $u, 'group_temperature')
	#else
            #set $threshold_t = weewx.units.ValueTuple(float($t), $u, 'group_temperature')
	#end if None
	#set $threshold_h = weewx.units.ValueHelper($threshold_t, converter=$converter)
	#set $t = $model.cutoff[0]
	#set $u = $model.cutoff[1]
	#if $t in ['None', 'none']
            #set $cutoff_t = weewx.units.ValueTuple(None, $u, 'group_temperature')
	#else
            #set $cutoff_t = weewx.units.ValueTuple(float($t), $u, 'group_temperature')
	#end if None
	#set $cutoff_h = weewx.units.ValueHelper($cutoff_t, converter=$converter)

        <tr><th align=right>deutsche Bezeichnung:</th><th align=left>$model.name_de</th></tr>
	<tr><th align=right>Standort:</th><th align=left>$station.location</th></tr>
	<tr><th align=right>letzte Berechnung:</th><th align=left>$run_date_h.format($now_format, add_label=False)</th></tr>
	<tr><th align=right>Model:</th><th align=left>$model.name_model</th></tr>
	<tr><th align=right>Schwelle/ Begin:</th><th align=left>$threshold_h.format()</th></tr>
	<tr><th align=right>Abbruch/ Ende:</th><th align=left>$cutoff_h.format()</th></tr>
        <tr><th align=right>Method:</th><th align=left>$model.method</th></tr>
        <tr><th align=right>Model Ref:</th><th align=left><a href="$model.ref">$model.ref</a></th></tr>
      </table>
      <br/>
      <table>
	#set $temp_unit = $unit.label.outTemp
	#set $gdd_unit = $unit.label.cooldeg
        <tr valign=top>
          <th align=left style="padding: 0px 10px 0px 10px">Datum</th>
          <th align=right style="padding: 0px 10px 0px 10px">Min<br>$temp_unit</th>
          <th align=right style="padding: 0px 10px 0px 10px">Max<br>$temp_unit</th>
          <th align=right style="padding: 0px 10px 0px 10px">DegDay<br>$gdd_unit</th>
          <th align=right style="padding: 0px 10px 0px 10px">Summe<br>$gdd_unit</th>
          <th align=left style="padding: 0px 10px 0px 10px">Ergebnis</th>
        </tr>
        #set $stages = $phenologies.get_development_stages_t($converter, $model.name_model)
	#set $month_offset = $phenologies.southern_hemisphere_start_month_offset
	#set $timespan = user.phenology.get_day_span($month_offset, $model.start_date, $latest_ts)
	#set $vectors = weewx.xtypes.get_series(obs_type=$model.name_model, timespan=$timespan, db_manager=$db_manager)
	#set $time_stamp_start_vt = $vectors[0]
	#set $time_stamp_stop_vt = $vectors[1]  
	#set $gdd_vt = $vectors[2]
	#set $gdd_sum = 0
	#set $time_stamp_start_values = $time_stamp_start_vt[0]
	#set $time_stamp_start_units = $time_stamp_start_vt[1:]
	#set $time_stamp_stop_values = $time_stamp_stop_vt[0]
	#set $gdd_values = $gdd_vt[0]
	#set $gdd_units = $gdd_vt[1:]
	#for $ndx_tuple in enumerate($time_stamp_start_values)
            #set $ndx = $ndx_tuple[0]
	    #set $time_stamp_start = $ndx_tuple[1]
	    #set $time_stamp_start_t = weewx.units.ValueTuple($time_stamp_start, *$time_stamp_start_units)
	    #set $time_stamp_stop = $time_stamp_stop_values[$ndx]
	    #set $time_stamp_stop_t = weewx.units.ValueTuple($time_stamp_stop, *$time_stamp_start_units)
	    #set $gdd = $gdd_values[$ndx]
	    #set $gdd_t = weewx.units.ValueTuple($gdd, *$gdd_units)
	    #set $gdd_lo = $gdd_sum
	    #set $gdd_sum += $gdd
	    #set $event = ""
	    #for $key_tuple in $stages.items()
	      #set $key = $key_tuple[0]
	      #set $val = $key_tuple[1]
	      #if not (None in [$val[0].value, $val[-1].value])
                #if ($gdd_lo < $val[0].value <= $gdd_sum) or ($gdd_lo < $val[-1].value <= $gdd_sum)
                  #set $event = '« {}'.format($key)
                #end if gdd_lo
	      #end if None
	    #end for key_tuple
	    #set $gdd_sum_t = weewx.units.ValueTuple($gdd_sum, *$gdd_units)
	    #set $day_span = weeutil.weeutil.TimeSpan($time_stamp_start, $time_stamp_stop)
	    #set $temp_min_t = weewx.xtypes.DailySummaries.get_aggregate('outTemp', $day_span, 'min', $db_manager)
	    #set $temp_max_t = weewx.xtypes.DailySummaries.get_aggregate('outTemp', $day_span, 'max', $db_manager)
	    #set time_stamp_start_h = weewx.units.ValueHelper($time_stamp_start_t, converter=$converter)
	    #set temp_min_h = weewx.units.ValueHelper($temp_min_t, converter=$converter)
	    #set temp_max_h = weewx.units.ValueHelper($temp_max_t, converter=$converter)
	    #set gdd_h = weewx.units.ValueHelper($gdd_t, converter=$converter)
	    #set gdd_sum_h = weewx.units.ValueHelper($gdd_sum_t, converter=$converter)
            #if $time_stamp_start < $earliest_ts
		#continue
	    #end if $earliest_ts			    
	<tr>
          <td align=left style="padding: 0px 10px 0px 10px">$time_stamp_start_h.format(format_string=$date_format)</td>
          <td align=right style="padding: 0px 10px 0px 10px">$temp_min_h.format(add_label=False)</td>
          <td align=right style="padding: 0px 10px 0px 10px">$temp_max_h.format(add_label=False)</td>
          <td align=right style="padding: 0px 10px 0px 10px">$gdd_h.format(add_label=False)</td>
          <td align=right style="padding: 0px 10px 0px 10px">$gdd_sum_h.format(add_label=False)</td>
          <td align=left style="padding: 0px 10px 0px 10px">$event</td>
        </tr>
	#end for ndx
      </table>
    </div>
   <hr />
#end for name_model

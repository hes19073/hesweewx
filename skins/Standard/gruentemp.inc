#encoding UTF-8
##  gruentemp.inc 2749 2017-03-13 18:15:24Z hes $

#set $Y = $current.dateTime.format("%Y")
#set $M = $current.dateTime.format("%m")
#set $B = $current.dateTime.format("%d")
#set $mo = 0
#set $gltakt = 0.0
#set $dayglt = 0.0
#set $glt200 = '25.03.2017'

#for $month in $year.months
    #set $mo += 1
    #for $day in $month.days
        #if $mo == 1
            #if $day.outTemp.avg.raw > 0.0
                 #set $dayglt = $day.outTemp.avg.raw * 0.5
            #else
                 #set $dayglt = 0
            #end if
        #elif $mo == 2
            #if $day.outTemp.avg.raw > 0.0
                 #set $dayglt = $day.outTemp.avg.raw * 0.75
            #else
                 #set $dayglt = 0
            #end if
        #elif $mo > 2
            #if $day.outTemp.avg.raw > 0.0
                 #set $dayglt = $day.outTemp.avg.raw
            #else
                 #set $dayglt = 0
            #end if
        #end if
        #set $gltakt += $dayglt
        ##if $gltakt >= 200.0 and $glt200 is None
            ##set $glt200 
        ##end if
    #end for
#end for
#set $gltaktformat = '%6.2f' % $gltakt 
#if $glt200 is None
    <td>Summe aktuell</td><td>$gltaktformat $unit.label.outTemp -tag</td>
  </tr><tr>
    <td>&nbsp;</td><td>&nbsp;</td>
#else
    <td>Summe aktuell</td><td>$gltaktformat $unit.label.outTemp -tag</td> 
   </tr><tr>
    <td>der Wert 200°C wurde erreicht am:</td><td>$glt200</td>
#end if


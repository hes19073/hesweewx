#encoding UTF-8
##  kaeltesumme.inc 2749 2017-03-13 18:15:24Z hes $

#set $Y = $current.dateTime.format("%Y")
#set $M = $current.dateTime.format("%m")
#set $B = $current.dateTime.format("%B")
#set $mo = 0
#set $mo1 = 0
#set $kssakt = 0.0
#set $daykss = 0.0

#for $year in $alltime.years
    $kss = $Y
    #for $month in $year.months
        #set $mo += 1
        #for $day in $month.days
            #if $mo < 4
                #if $day.outTemp.avg.raw is not None
                    #if $day.outTemp.avg.raw < 0.0
                         #set $daykss = $day.outTemp.avg.raw
                    #else
                         #set $daykss = 0
                    #end if
                #else
                    #set $daykss = 0
                #end if
            #end if
            #set $kssakt = $kssakt + $daykss
        #end for
    #end for
    #for $month in $year1.months
        #set $mo1 += 1
        #for $day in $month.days
            #if $mo1 >= 11
                #if $day.outTemp.avg.raw is not None
                    #if $day.outTemp.avg.raw < 0.0                                 
                         #set $daykss = $day.outTemp.avg.raw   
                    #else
                         #set $daykss = 0
                    #end if
                #else
                    #set $daykss = 0
                #end if
            #end if
            #set $kssakt = $kssakt + $daykss
            #set $kssy = $kss + $year
        #end for
    #end for
    #set $kssakt1 = abs($kssakt)
    #set $kssaktformat = '%6.1f' % $kssakt1 + " Gradtag"
    <tr><td>Summe $kss</td><td>$kssaktformat</td></tr>
#end for
  <tr><td>&nbsp;</td><td>&nbsp;</td></tr>
#if $kssakt1 < 100
     <tr><td>Summe < 100</td><td>sehr milder Winter</td>
#elif $kssakt1 > 100 and $kssakt1 <= 200
     <tr><td> 100 - 200 </td><td>normaler Winter</td>
#elif $kssakt1 > 200 and $kssakt1 <= 300
     <tr><td> 200 - 300 </td><td>mäßig strenger Winter</td>
#elif $kssakt1 > 300 and $kssakt1 <= 400
     <tr><td> 300 - 400 </td><td>strenger Winter</td>
#elif $kssakt1 > 400 
     <tr><td>Summe > 400</td><td>sehr strenger Winter</td>
#end if

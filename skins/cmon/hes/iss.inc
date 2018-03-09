## isswatch for weewx - Copyright 2016 Chris Davies-Barnard
#errorCatcher Echo
#encoding UTF-8
<!-- The next sighting -->
<div class="iss">
<div>
 <p>Die Sichtungen der internationale Raumstation <strong>$issnext.title</strong>&nbsp;um&nbsp;<strong>$issnext.time</strong> am <strong>$issnext.date</strong></p>
 <p>Sie wird sichtbar sein für&nbsp;$issnext.duration,&nbsp;zirka&nbsp;$issnext.approach&nbsp;und abfliegenden&nbsp;$issnext.departure.  
 Die Raumstation wird ein maximale Höhe von&nbsp;$issnext.maximumelevation&nbsp;über dem Horizon haben.<br />
 Weiteres unter <a href="$issnext.guid">http://spotthestation.nasa.gov/</a>.</p>
</div>
		
<!-- All the sightings -->
<table class="gridtable">
 <tr>
  <th>&nbsp;</th>
   <th title="Published Time Stamp">Datum</th>
   <th>Zeit</th>
   <th>Was ist sichtbar?</th>
   <th>Wie lange?</th>
   <th>Anflug von</th>
   <th>Maximale Höhe<br /><strong>Elevation</strong></th>
   <th>Abflug unter</th>
 </tr>
#for $sighting in $issall
 <tr>
  <td><a href="$sighting.guid">&#9741;</a></td>
  <td>$sighting.date</td>
  <td>$sighting.time</td>
  <td>$sighting.title</td>
  <td>$sighting.duration</td>
  <td>$sighting.approach</td>
  <td>$sighting.maximumelevation</td>
  <td>$sighting.departure</td>
 </tr>
#end for
</table>
</div>

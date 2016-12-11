<?php

header('Content-Type: image/jpeg');

//int strtotime ( string $time [, int $now ] )
// $ sudo apt-get install php5-gd beachten
// Wieviel Uhr?
$ts = strtotime("now");

// Berechne einige Konstanten im Voraus:
// Zeitgleichung in Minuten
$zg = 1*3600*(-0.1752*sin(0.033430 * gmdate("z",$ts) + 0.5474) - 0.1340*sin(0.018234*gmdate("z",$ts) - 0.1939));
if ($zg<0){
    $ts=strtotime("now ".(int)$zg." second",$ts);
}else{
    $ts=strtotime("+ ".(int)$zg." second",$ts);
}    
// Jahr und Tag berechnen (zwischen 0 und 2 Pi)
$tagg = ((gmdate("H",$ts)*60+gmdate("i",$ts))*60+gmdate("s",$ts))/43200*pi();
$jahr = (gmdate("z",$ts)-79.25)/365*2*pi();
// Erdachse steht um 23.5° schief:
$alpha= 0.41015237422;
$cosalpha = cos($alpha);
$sinalpha = sin($alpha);
$cosjahr  = cos($jahr);
$sinjahr  = sin($jahr);

// Berechne Winkel, under dem die Sonne zu sehen ist
function angle($l,$b){
    // Breite b und Länge l werden in Grad erwartet
    global $tagg, $cosalpha, $sinalpha, $cosjahr, $sinjahr;
    // Bogenmaßumrechnung
    $b    = (90-$b)/180*pi();
    $tag  = $tagg-$l/180*pi();
    // Zenitvektor an der Oberfläche ohne schiefe Erdachse
    // Sonne steht in Richtung der positiven x-Achse, Erdrotation noch in Richtung der z-Achse
    $sinb = sin($b);
    $r    = array(-1*cos($tag)*$sinb,sin($tag)*$sinb,cos($b));
    // Erdachse dreht sich zusätzlich im Verlauf des Jahres, darum die etwas
    // komplizierte Drehmatrix um eine beliebige Drehachse r mit z=0 und |r|=1
    //$matrix = array(array((1-cos($alpha))*cos($jahr)*cos($jahr)+cos($alpha) ,
    //              (1-cos($alpha))*cos($jahr)*sin($jahr),
    //               -1*sin($alpha)*sin($jahr)),
        //        array((1-cos($alpha))*cos($jahr)*sin($jahr),
    //              (1-cos($alpha))*sin($jahr)*sin($jahr)+cos($alpha),
    //              (1-cos($alpha))*cos($jahr)*sin($jahr)),
    //            array(sin($alpha)*sin($jahr),
    //              -1*sin($alpha)*cos($jahr),
    //              cos($alpha)));

    // Führe Drehung aus (berechne nur den wichtigen x-Wert:
    return $r[0] * ((1-$cosalpha)*$cosjahr*$cosjahr+$cosalpha)
            + $r[1] * (1-$cosalpha)*$cosjahr*$sinjahr
            - $r[2] * $sinalpha*$sinjahr;
}

// Einlesen der Bilder aus Dateien:
$inputfile_day = "./land_ocean_ice_800.jpg";
$inputfile_night = "./land_ocean_ice_lights_800.jpg";
$size = getimagesize ( $inputfile_day );
$im = imagecreatefromjpeg ( $inputfile_day );
$im2 = imagecreatefromjpeg ( $inputfile_night );
$col = imagecolorallocate ( $im,255,0,0 );
$col2 = imagecolorallocate ( $im,55,55,55 );

// Pixelgröße (je kleiner, desto langsamer)
$blocksize = 2;
for($i=0;$i<$size[0];$i=$i+$blocksize){
  for($j=0;$j<$size[1];$j=$j+$blocksize){
    $x = angle(180-($i/$size[0]*360),-90+($j/$size[1]*180));
    if ($x<-0.11){
        ImageCopy($im,$im2,$i,$j,$i,$j,$blocksize,$blocksize);
    }elseif($x<0){    
        $offset = 13;
        $ptc = (int)(100-($x+0.11)/(0.11)*(100-$offset))+$offset;
        if($ptc>100){$ptc=100;}
        ImageCopyMerge($im,$im2,$i,$j,$i,$j,$blocksize,$blocksize,$ptc);
    }
  }
}

// Ausgabe in Datei:
$im3 = imagecreatetruecolor(800,100);
imagecopy($im3,$im,0,0,0,50,800,100);
imagestring($im,2,5,1,gmdate("d.m.Y H:i:s ")."UTC",$col);
imagestring($im,2,675,1,"http://wetter.hes61.de",$col);
imagejpeg ($im, NULL, 95);
imagejpeg ($im3, NULL, 90);
imagejpeg ($im3, NULL, 90);

?>

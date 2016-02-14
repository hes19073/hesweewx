<?php 
// Version 3.02 - 01-Nov-2014 - fixes for other WU Page URL types like locid:, US City, others
//
$Version = "WU-forecast.php (ML) Version 3.02 - 01-Nov-2014";
//
// error_reporting(E_ALL);  // uncomment to turn on full error reporting
//
// script available at http://saratoga-weather.org/scripts.php
//  
// you may copy/modify/use this script as you see fit,
// no warranty is expressed or implied.
//
// This script parses the WeatherUnderground forecast JSON API and loads icons/text into
//  arrays so you can use them in your weather website.  
//
// NOTE: You must leave an attribution link to weatherunderground.com in the output page.
//
// output: creates XHTML 1.0-Strict HTML page (or inclusion)
//
// Options on URL:
//
//   inc=Y            - omit <HTML><HEAD></HEAD><BODY> and </BODY></HTML> from output
//   heading=n        - (default)='y' suppress printing of heading (forecast city/by/date)
//   icons=n          - (default)='y' suppress printing of the icons+conditions+temp+wind+UV
//   text=n           - (default)='y' suppress printing of the periods/forecast text
//
//
//  You can also invoke these options directly in the PHP like this
//
//    $doIncludeWU = true;
//    include("WU-forecast.php");  for just the text
//  or ------------
//    $doPrintWU = false;
//    include("WU-forecast.php");  for setting up the $WUforecast... variables without printing
//
//  or ------------
//    $doIncludeWU = true;
//    $doPrintHeadingWU = true;
//    $doPrintIconsWU = true;
//    $doPrintTextWU = false
//    include("WU-forecast.php");  include mode, print only heading and icon set
//
// Variables returned (useful for printing an icon or forecast or two...)
//
// $WUforecastcity 		- Name of city from WU Forecast header
//
// The following variables exist for $i=0 to $i= number of forecast periods minus 1
//  a loop of for ($i=0;$i<count($WUforecastday);$i++) { ... } will loop over the available 
//  values.
//
// $WUforecastday[$i]	- period of forecast
// $WUforecasttext[$i]	- text of forecast 
// $WUforecasttemp[$i]	- Temperature with text and formatting
// $WUforecastpop[$i]	- Number - Probabability of Precipitation ('',10,20, ... ,100)
// $WUforecasticon[$i]   - base name of icon graphic to use
// $WUforecastcond[$i]   - Short legend for forecast icon 
// $WUforecasticons[$i]  - Full icon with Period, <img> and Short legend.
//
// Settings ---------------------------------------------------------------
//REQUIRED: a WU API KEY.. sign up at http://www.wunderground.com/weather/api/
$WUAPIkey = '71eae8c9193378cb'; // use this only for standalone / non-template use
// NOTE: if using the Saratoga template, add to Settings.php a line with:
//    $SITE['WUAPIkey'] = 'your-api-key-here';
// and that will enable the script to operate correctly in your template
//
$iconDir ='images/';	// directory for carterlake icons './forecast/images/'
$iconType = '.jpg';				// default type='.jpg' 
//                            		use '.gif' for animated icons from http://www.meteotreviglio.com/
//$iconDir ='';					// set to '' to use the Wunderground icons instead
//
//
//$WU_URL = 'http://www.wunderground.com/global/stations/06075.html';
$WU_URL = 'http://www.wunderground.com/cgi-bin/findweather/getForecast?query=pws:IMECKLEN20';
//
// The optional multi-city forecast .. make sure the first entry is for the $WU_URL location
// The contents will be replaced by $SITE['WUforecasts'] if specified in your Settings.php

/*

$WUforecasts = array(
 // Location|forecast-URL  (separated by | characters)
'Saratoga|http://www.wunderground.com/cgi-bin/findweather/getForecast?query=95070',
'Aarhus|http://www.wunderground.com/global/stations/06075.html',
'Auckland|http://english.wunderground.com/cgi-bin/findweather/getForecast?query=-36.910%2C174.771&sp=IAUCKLAN110', // Awhitu, Waiuku New Zealand
'Amsterdam|http://www.wunderground.com/cgi-bin/findweather/getForecast?query=Amsterdam%2C+Netherlands',
'Paris|http://www.wunderground.com/cgi-bin/findweather/getForecast?query=Paris%2C+France',
'Stockholm|http://www.wunderground.com/cgi-bin/findweather/getForecast?query=Stockholm%2C+Sweden',
'Oslo|http://www.wunderground.com/cgi-bin/findweather/getForecast?query=Oslo%2C+Norway',
'Moscow|http://www.wunderground.com/global/stations/27612.html',
'Athens|http://www.wunderground.com/cgi-bin/findweather/getForecast?query=Athens%2C+Greece',
'Tel Aviv|http://www.wunderground.com/cgi-bin/findweather/getForecast?query=Tel+Aviv%2C+Israel',
'Madrid|http://www.wunderground.com/cgi-bin/findweather/getForecast?query=Madrid%2C+Spain',
'Helsinki|http://www.wunderground.com/cgi-bin/findweather/getForecast?query=Helsinki%2C+Finland',
'Castrop-Rauxel|http://www.wunderground.com/cgi-bin/findweather/getForecast?query=51.572%2C7.376&sp=INORDRHE72',
'Southampton|http://www.wunderground.com/global/stations/03865.html',
'Canvey Island, Essex|http://www.wunderground.com/weather-forecast/zmw:00000.57.03691',
'Saratoga PWS|http://www.wunderground.com/cgi-bin/findweather/getForecast?query=pws:KCASARAT1',
'St. Nicholas|http://www.wunderground.com/q/locid:UKEN1390',
'Alberta (Canada)|http://www.wunderground.com/q/locid:CAXX4520',
'Andover (Middle Wallop)|http://www.wunderground.com/cgi-bin/findweather/getForecast?query=zmw:00000.1.03749',
'Assen (Holland)|http://www.wunderground.com/q/zmw:00000.6.06280',
'Honolulu|http://www.wunderground.com/US/HI/Honolulu.html',
'Malta|http://www.wunderground.com/global/ML.html',
); 
//*/
//
$maxWidth = '640px';                      // max width of tables (could be '100%')
$maxIcons = 10;                           // max number of icons to display
$maxForecasts = 14;                       // max number of Text forecast periods to display
$maxForecastLegendWords = 4;              // more words in forecast legend than this number will use our forecast words 
$numIconsInFoldedRow = 5;                 // if words cause overflow of $maxWidth pixels, then put this num of icons in rows
$autoSetTemplate = true;                  // =true set icons based on wide/narrow template design
$cacheFileDir = './';                     // default cache file directory
$cacheName = "WU-forecast-json.txt";      // locally cached page from WU
$refetchSeconds = 3600;                   // cache lifetime (3600sec = 60 minutes)
$xlateCOP = 'Chance of precipitation';    // change to local language if needed like
//$xlateCOP = 'Kans op neerslag';   //  Dutch example
$showTempsAs  = 'C';                  // under icons/forecast, 'C'=Centigrade, 'F'=Fahrenheit
//$charsetOutput = 'ISO-8859-1';        // default character encoding of output
$charsetOutput = 'utf8';
$lang = 'de';	// default language
$foldIconRow = true;  // display icons in rows of 5 if long texts are found
$RTLlang = ',he,jp,cn,';  // languages that use right-to-left order
// ---- end of settings ---------------------------------------------------

// overrides from Settings.php if available
global $SITE;
if (isset($SITE['WUforecasts']))   {$WUforecasts = $SITE['WUforecasts']; }
if (isset($SITE['WUAPIkey']))	{$WUAPIkey = $SITE['WUAPIkey']; } // new V3.00
if (isset($SITE['fcsturlWU'])) 	{$WU_URL = $SITE['fcsturlWU'];}
if (isset($SITE['fcsticonsdir'])) 	{$iconDir = $SITE['fcsticonsdir'];}
if (isset($SITE['fcsticonstype'])) 	{$iconType = $SITE['fcsticonstype'];}
if (isset($SITE['uomTemp']))	{$uomTemp = $SITE['uomTemp'];}
if (isset($SITE['xlateCOP']))	{$xlateCOP = $SITE['xlateCOP'];}
if (isset($LANGLOOKUP['Chance of precipitation'])) {
  $xlateCOP = $LANGLOOKUP['Chance of precipitation'];
}
if (isset($SITE['charset']))	{$charsetOutput = strtoupper($SITE['charset']); }
if (isset($SITE['lang']))		{$lang = $SITE['lang'];}
if(isset($SITE['cacheFileDir']))     {$cacheFileDir = $SITE['cacheFileDir']; }
if(isset($SITE['foldIconRow']))     {$foldIconRow = $SITE['foldIconRow']; }
if(isset($SITE['RTL-LANG']))     {$RTLlang = $SITE['RTL-LANG']; }
// end of overrides from Settings.php
//
// -------------------begin code ------------------------------------------


if (isset($_REQUEST['sce']) && strtolower($_REQUEST['sce']) == 'view' ) {
   //--self downloader --
   $filenameReal = __FILE__;
   $download_size = filesize($filenameReal);
   header('Pragma: public');
   header('Cache-Control: private');
   header('Cache-Control: no-cache, must-revalidate');
   header("Content-type: text/plain");
   header("Accept-Ranges: bytes");
   header("Content-Length: $download_size");
   header('Connection: close');
   
   readfile($filenameReal);
   exit;
}

$Status = "<!-- $Version on PHP ".phpversion()." -->\n";
//------------------------------------------------

if(preg_match('|specify|i',$WUAPIkey)) {
	print "<p>Note: the WU-forecast.php script requires an API key from WeatherUnderground to operate.<br/>";
	print "Visit <a href=\"http://www.wunderground.com/weather/api/\">Weather Underground</a> to ";
	print "register for an API key.</p>\n";
	if( isset($SITE['fcsturlWU']) ) {
		print "<p>Insert in Settings.php an entry for:<br/><br/>\n";
		print "\$SITE['WUAPIkey'] = '<i>your-key-here</i>';<br/><br/>\n";
		print "replacing <i>your-key-here</i> with your WU API key.</p>\n";
	}
	return;
}

$NWSiconlist = array(
 // WU Icon name => NWS icon name // WU meaning
 'chanceflurries.gif' 	=> array('sn.jpg','Chance flurries'), // Chance of Flurries
 'chancerain.gif' 		=> array('hi_shwrs.jpg','Chance rain'), // Chance of Rain
 'chancesleet.gif' 		=> array('ip.jpg','Chance sleet'), // Chance of Sleet
 'chancesnow.gif' 		=> array('sn.jpg','Chance snow'), // Chance of Snow
 'chancetstorms.gif' 	=> array('hi_tsra.jpg','Chance thunderstorms'), // Chance of Thunderstorms
 'clear.gif' 			=> array('skc.jpg','Clear'), // Clear
 'cloudy.gif' 			=> array('ovc.jpg','Cloudy'), // Cloudy
 'flurries.gif' 		=> array('sn.jpg','Flurries'), // Flurries
 'fog.gif' 				=> array('fg.jpg','Fog'), // Fog
 'hazy.gif' 			=> array('fg.jpg','Hazy'), // Hazy
 'mostlycloudy.gif' 	=> array('bkn.jpg','Mostly cloudy'), // Mostly Cloudy
 'mostlysunny.gif' 		=> array('sct.jpg','Partly cloudy'), // Mostly Sunny
 'partlycloudy.gif' 	=> array('sct.jpg','Partly cloudy'), // Partly Cloudy
 'partlysunny.gif' 		=> array('bkn.jpg','Mostly sunny'), // Partly Sunny
 'rain.gif' 			=> array('ra.jpg','Rain'), // Rain 
 'sleet.gif' 			=> array('ip.jpg','Sleet'), // Sleet
 'sleat.gif' 			=> array('ip.jpg','Sleet'), // Sleet (other spelling)
 'snow.gif' 			=> array('sn.jpg','Snow'), // Snow
 'sunny.gif' 			=> array('skc.jpg','Sunny'), // Sunny
 'tstorms.gif' 			=> array('tsra.jpg','Thunderstorms'), // Thunderstorms
 'unknown.gif' 			=> array('na.jpg',''), // Unknown
 'nt_chanceflurries.gif' => array('nsn.jpg','Chance flurries'), // Chance of Flurries
 'nt_chancerain.gif' 	=> array('hi_nshwrs.jpg','Chance rain'), // Chance of Rain
 'nt_chancesleet.gif' 	=> array('ip.jpg','Chance sleet'), // Chance of Sleet
 'nt_chancesnow.gif' 	=> array('nsn.jpg','Chance snow'), // Chance of Snow
 'nt_chancetstorms.gif' => array('hi_ntsra.jpg','Chance thunderstorms'), // Chance of Thunderstorms
 'nt_clear.gif' 		=> array('nskc.jpg','Clear'), // Clear
 'nt_cloudy.gif' 		=> array('novc.jpg','Cloudy'), // Cloudy
 'nt_flurries.gif' 		=> array('nsn.jpg','Flurries'), // Flurries
 'nt_fog.gif' 			=> array('nfg.jpg','Fog'), // Fog
 'nt_hazy.gif' 			=> array('nfg.jpg','Hazy'), // Hazy
 'nt_mostlycloudy.gif' 	=> array('nbkn.jpg','Mostly cloudy'), // Mostly Cloudy
 'nt_mostlysunny.gif' 	=> array('nsct.jpg','Partly cloudy'), // Mostly Sunny
 'nt_partlycloudy.gif' 	=> array('nsct.jpg','Partly cloudy'), // Partly Cloudy
 'nt_partlysunny.gif' 	=> array('nbkn.jpg','Mostly cloudy'), // Partly Sunny
 'nt_rain.gif' 			=> array('nra.jpg','Rain'), // Rain 
 'nt_sleet.gif' 		=> array('ip.jpg','Sleet'), // Sleet
 'nt_sleat.gif'			=> array('ip.jpg','Sleet'), // sleet (other spelling)
 'nt_snow.gif' 			=> array('nsn.jpg','Snow'), // Snow
 'nt_sunny.gif' 		=> array('nskc.jpg','Sunny'), // Sunny
 'nt_tstorms.gif' 		=> array('ntsra.jpg','Thunderstorms'), // Thunderstorms
 'nt_unknown.gif' 		=> array('na.jpg',''), // Unknown
 '.gif' 		        => array('na.jpg',''), // Unknown
) ;
//
/* translation entries needed:

langlookup|Chance flurries|Chance flurries|
langlookup|Chance rain|Chance rain|
langlookup|Chance sleet|Chance sleet|
langlookup|Chance snow|Chance snow|
langlookup|Chance thunderstorms|Chance thunderstorms|
langlookup|Clear|Clear|
langlookup|Cloudy|Cloudy|
langlookup|Flurries|Flurries|
langlookup|Fog|Fog|
langlookup|Hazy|Hazy|
langlookup|Mostly cloudy|Mostly cloudy|
langlookup|Partly cloudy|Partly cloudy|
langlookup|Mostly sunny|Mostly sunny|
langlookup|Rain|Rain|
langlookup|Sleet|Sleet|
langlookup|Snow|Snow|
langlookup|Sunny|Sunny|
langlookup|Thunderstorms|Thunderstorms|

*/

if(!function_exists('langtransstr')) {
	// shim function if not running in template set
	function langtransstr($input) { return($input); }
}

if(!function_exists('json_last_error')) {
	// shim function if not running PHP 5.3+
	function json_last_error() { return('- N/A'); }
	$Status .= "<!-- php V".phpversion()." json_last_error() stub defined -->\n";
	if(!defined('JSON_ERROR_NONE')) { define('JSON_ERROR_NONE',0); }
	if(!defined('JSON_ERROR_DEPTH')) { define('JSON_ERROR_DEPTH',1); }
	if(!defined('JSON_ERROR_STATE_MISMATCH')) { define('JSON_ERROR_STATE_MISMATCH',2); }
	if(!defined('JSON_ERROR_CTRL_CHAR')) { define('JSON_ERROR_CTRL_CHAR',3); }
	if(!defined('JSON_ERROR_SYNTAX')) { define('JSON_ERROR_SYNTAX',4); }
	if(!defined('JSON_ERROR_UTF8')) { define('JSON_ERROR_UTF8',5); }
}

WU_loadLangDefaults (); // set up the language defaults
$WULANG = 'EN'; // Default to English for API
$lang = strtolower($lang); 	
if( isset($WUlanguages[$lang]) ) { // if $lang is specified, use it
	$SITE['lang'] = $lang;
	$WULANG = $WUlanguages[$lang];
	$charsetOutput = (isset($WUlangCharsets[$lang]))?$WUlangCharsets[$lang]:$charsetOutput;
}

if(isset($_GET['lang']) and isset($WUlanguages[strtolower($_GET['lang'])]) ) { // template override
	$lang = strtolower($_GET['lang']);
	$SITE['lang'] = $lang;
	$WULANG = $WUlanguages[$lang];
	$charsetOutput = (isset($WUlangCharsets[$lang]))?$WUlangCharsets[$lang]:$charsetOutput;
}

$doRTL = (strpos($RTLlang,$lang) !== false)?true:false;  // format RTL language in Right-to-left in output

// get the selected forecast location code
$haveIndex = '0';
if (!empty($_GET['z']) && preg_match("/^[0-9]+$/i", htmlspecialchars($_GET['z']))) {
  $haveIndex = htmlspecialchars(strip_tags($_GET['z']));  // valid zone syntax from input
} 

if(!isset($WUforecasts[0])) {
	// print "<!-- making NWSforecasts array default -->\n";
	$WUforecasts = array("|$WU_URL"); // create default entry
}

//  print "<!-- NWSforecasts\n".print_r($WUforecasts,true). " -->\n";
// Set the default zone. The first entry in the $SITE['NWSforecasts'] array.
list($Nl,$Nn) = explode('|',$WUforecasts[0].'|||');
$FCSTlocation = $Nl;
$WU_URL = $Nn;

if(!isset($WUforecasts[$haveIndex])) {
	$haveIndex = 0;
}

// locations added to the drop down menu and set selected zone values
$dDownMenu = '';
for ($m=0;$m<count($WUforecasts);$m++) { // for each locations
  list($Nlocation,$Nname) = explode('|',$WUforecasts[$m].'|||');
  $seltext = '';
  if($haveIndex == $m) {
    $FCSTlocation = $Nlocation;
    $WU_URL = $Nname;
	$seltext = ' selected="selected" ';
  }
  $dDownMenu .= "     <option value=\"$m\"$seltext>".langtransstr($Nlocation)."</option>\n";
}

// build the drop down menu
$ddMenu = '';
// create menu if at least two locations are listed in the array
if (isset($WUforecasts[0]) and isset($WUforecasts[1])) {
	if($doRTL) {$RTLopt = ' style="direction: rtl;"'; } else {$RTLopt = '';}; 
	$ddMenu .= '<tr align="center">
      <td style="font-size: 14px; font-family: Arial, Helvetica, sans-serif">
      <script type="text/javascript">
        <!--
        function menu_goto( menuform ){
         selecteditem = menuform.logfile.selectedIndex ;
         logfile = menuform.logfile.options[ selecteditem ].value ;
         if (logfile.length != 0) {
          location.href = logfile ;
         }
        }
        //-->
      </script>
     <form action="" method="get">
     <p><select name="z" onchange="this.form.submit()"'.$RTLopt.'>
     <option value=""> - '.langtransstr('Select Forecast').' - </option>
' . $dDownMenu .
		$ddMenu . '     </select></p>
     <div><noscript><pre><input name="submit" type="submit" value="'.langtransstr('Get Forecast').'" /></pre></noscript></div>
     </form>
    </td>
   </tr>
';
}

$Force = false;

if (isset($_REQUEST['force']) and  $_REQUEST['force']=="1" ) {
  $Force = true;
}

$doDebug = false;
if (isset($_REQUEST['debug']) and strtolower($_REQUEST['debug'])=='y' ) {
  $doDebug = true;
}

$fileName = $WU_URL;
if ($doDebug) {
  $Status .= "<!-- WU URL: $fileName -->\n";
}

if (isset($uomTemp) and $showTempsAs <> 'B') { // use Settings.php Temp units only
   $showTempsAs = preg_match('|C|i',$uomTemp) ? 'C' : 'F';
   $Status .= "<!-- temps in $showTempsAs -->\n";
}

if ($autoSetTemplate and isset($_SESSION['CSSwidescreen'])) {
	if($_SESSION['CSSwidescreen'] == true) {
	   $maxWidth = '900px';
	   $maxIcons = 14;
	   $maxForecasts = 14;
	   $numIconsInFoldedRow = 7;
	   $Status .= "<!-- autoSetTemplate using ".$SITE['CSSwideOrNarrowDefault']." aspect. -->\n";	
	}
	if($_SESSION['CSSwidescreen'] == false) {
	   $maxWidth = '640px';
	   $maxIcons = 10;
	   $maxForecasts = 14;
	   $numIconsInFoldedRow = 5;
	   $Status .= "<!-- autoSetTemplate using ".$SITE['CSSwideOrNarrowDefault']." aspect. -->\n";	
	}
}

$cacheName = $cacheFileDir . $cacheName;
$cacheName = preg_replace('|\.txt|is',"-$haveIndex-$lang.txt",$cacheName); // unique cache per language used

$APIfileName = WU_get_APIURL($fileName); // transform WU page URL to API query URL

if (! $Force and file_exists($cacheName) and filemtime($cacheName) + $refetchSeconds > time()) {
      $html = implode('', file($cacheName)); 
      $Status .= "<!-- loading from $cacheName (" . strlen($html) . " bytes) -->\n"; 
  } else { 
      $Status .= "<!-- loading from $APIfileName. -->\n"; 
      $html = WU_fetchUrlWithoutHanging($APIfileName,$cacheName); 
	  
    $RC = '';
	if (preg_match("|^HTTP\/\S+ (.*)\r\n|",$html,$matches)) {
	    $RC = trim($matches[1]);
	}
	$Status .= "<!-- RC=$RC, bytes=" . strlen($html) . " -->\n";
	if (preg_match('|30\d |',$RC)) { // handle possible blocked redirect
	   preg_match('|Location: (\S+)|is',$html,$matches);
	   if(isset($matches[1])) {
		  $sURL = $matches[1];
		  if(preg_match('|opendns.com|i',$sURL)) {
			  $Status .= "<!--  NOT following to $sURL --->\n";
		  } else {
			$Status .= "<!-- following to $sURL --->\n";
		
			$html = WU_fetchUrlWithoutHanging($sURL,false);
			$RC = '';
			if (preg_match("|^HTTP\/\S+ (.*)\r\n|",$html,$matches)) {
				$RC = trim($matches[1]);
			}
			$Status .= "<!-- RC=$RC, bytes=" . strlen($html) . " -->\n";
		  }
	   }
    }
      $fp = fopen($cacheName, "w"); 
	  if (!$fp) { 
	    $Status .= "<!-- unable to open $cacheName for writing. -->\n"; 
	  } else {
        $write = fputs($fp, $html); 
        fclose($fp);  
		$Status .= "<!-- saved cache to $cacheName (". strlen($html) . " bytes) -->\n";
	  } 
} 


  preg_match('|charset="{0,1}(\S+)"{0,1}|i',$html,$matches);
  
  if (isset($matches[1])) {
    $charsetInput = strtoupper($matches[1]);
  } else {
    $charsetInput = 'UTF-8';
  }
  
 $doIconv = ($charsetInput == $charsetOutput)?false:true; // only do iconv() if sets are different
 
 $Status .= "<!-- using charsetInput='$charsetInput' charsetOutput='$charsetOutput' doIconv='$doIconv' doRTL='$doRTL' -->\n";

  $i = strpos($html,"\r\n\r\n");
  $headers = substr($html,0,$i-1);
  $content = substr($html,$i+4);
  if(preg_match('|Transfer-Encoding: chunke|Ui',$headers)) {
	  $Status .= "<!-- unchunking response -->\n"; 
	  $Status .= "<!-- in=".strlen($html);
      $html = preg_replace("|\r\n[0-9a-fA-F]+\r\n|is",'',$html); // kludge, but should get them all :)
	  $Status .= " out=".strlen($html). " bytes -->\n";
	}


 //  process the file .. select out the 7-day forecast part of the page
  $UnSupported = false;

// --------------------------------------------------------------------------------------------------
  
 $Status .= "<!-- processing JSON entries for forecast -->\n";
  $i = strpos($html,"\r\n\r\n");
  $headers = substr($html,0,$i-1);
  $content = substr($html,$i+4);
 

  $rawJSON = $content;
  $Status .= "<!-- rawJSON size is ".strlen($rawJSON). " bytes -->\n";

  $rawJSON = WU_prepareJSON($rawJSON);
  $JSON = json_decode($rawJSON,true); // get as associative array
  $Status .= WU_decode_JSON_error();
  //$Status .= "<!-- JSON\n".print_r($JSON,true)." -->\n";

/* //Ken's dump debugging code
$Status = htmlentities($Status);
$Status = preg_replace("|\n|is","<br/>\n",$Status);
print $Status;
return;
//Ken's dump debugging code
*/ 
if(json_last_error() === JSON_ERROR_NONE) { // got good JSON .. process it
   $UnSupported = false;

   $WUforecastcity = trim(trim($JSON['location']['city']));
   if($doIconv) {$WUforecastcity = iconv($charsetInput,$charsetOutput.'//TRANSLIT',$WUforecastcity);}
   if($doDebug) {
     $Status .= "<!-- WUforecastcity='$WUforecastcity' -->\n";
   }
   $WUtitle = "5-day Forecast";

// Process the Period forecasts for High/Low temperatures (one period=1 day)
// much easier than extracting from the text forecast :)
  $n = 0;
  foreach ($JSON['forecast']['simpleforecast']['forecastday'] as $i => $FCpart) {
	  $sT = ($showTempsAs == 'C')?'celsius':'fahrenheit';
	  $WUforecasttemp[$n] = "<span style=\"color: #ff0000;\">".$FCpart['high'][$sT]."&deg;$showTempsAs</span>";
	  $n++;
	  $WUforecasttemp[$n] = "<span style=\"color: #0000ff;\">".$FCpart['low'][$sT]."&deg;$showTempsAs</span>";
	  $n++;
  }

// process the forecast details from the 1/2 day periods (day, night, etc)
  $n = 0; 
  foreach ($JSON['forecast']['txt_forecast']['forecastday'] as $i => $FCpart) {  // 
 	if ( $doDebug) {
      $Status .= "<!-- processing forecastday[$i]='" . $FCpart['title'] . "' -->\n";
	}
	$sT = ($showTempsAs == 'C')?'fcttext_metric':'fcttext';	
    if($i >= $maxForecasts or strlen($FCpart['title'])+strlen($FCpart[$sT]) < 10) {
		break; // end of the good stuff
	}

	$WUforecasticon[$n] = $FCpart['icon'].'.gif';
	if ($doDebug) {
      $Status .= "<!-- WUforecasticon[$n]='" . $WUforecasticon[$n] . "' -->\n";
	}	

	$WUforecastday[$n] = trim($FCpart['title']);
	if($doIconv) {$WUforecastday[$n] = iconv($charsetInput,$charsetOutput.'//TRANSLIT',$WUforecastday[$n]);}
	$WUforecasttitles[$n] = $WUforecastday[$n];
	if ($doDebug) {
      $Status .= "<!-- WUforecastday[$n]='" . $WUforecastday[$n] . "' -->\n";
	}	

	$WUforecasttext[$n] = trim($FCpart[$sT]);
	if($doIconv) {$WUforecasttext[$n] = preg_replace('/(Chance of Precip.|Chance of precipitation:)/s',iconv($charsetOutput,$charsetInput,$xlateCOP).':',$WUforecasttext[$n]);}
	if($doIconv) {$WUforecasttext[$n] = iconv($charsetInput,$charsetOutput.'//TRANSLIT',$WUforecasttext[$n]);}
	if ($doDebug) {
      $Status .= "<!-- WUforecasttext[$n]='" . $WUforecasttext[$n] . "' -->\n";
	}
	
	$WUforecastpop[$n] = $FCpart['pop'];
	if ($doDebug) {
      $Status .= "<!-- WUforecastpop[$n]='" . $WUforecastpop[$n] . "' -->\n";
	}

	$temp = explode('.',$WUforecasttext[$n]); // split as sentences (sort of).
	
	$WUforecastcond[$n] = trim($temp[0]); // take first one as summary.
	if ($doDebug) {
      $Status .= "<!-- forecastcond[$n]='" . $WUforecastcond[$n] . "' -->\n";
	}
    if (count(explode(' ',$WUforecastcond[$n])) > $maxForecastLegendWords) {
	   if(function_exists('langtransstr')) {
         $WUforecastcond[$n] = langtransstr($NWSiconlist[$WUforecasticon[$n]][1]); // use our description instead
	   } else {
         $WUforecastcond[$n] = $NWSiconlist[$WUforecasticon[$n]][1]; // use our description instead
	   }
	   $Status .= "<!-- replaced forecastcond[$n]='" . $WUforecastcond[$n] . "' -->\n";
    }

	$WUforecasticons[$n] = $WUforecastday[$n] . "<br/>" .
	     WU_img_replace($WUforecasticon[$n],$WUforecastcond[$n],$WUforecastpop[$n]) . "<br/>" .
		 $WUforecastcond[$n];
	$n++;
  } // end of process text forecasts

  
 
} // end got good JSON decode/process
  
// end process JSON style --------------------------------------------------------------------

// All finished with parsing, now prepare to print

  $wdth = intval(100/count($WUforecasticons));
  $ndays = intval(count($WUforecasticon)/2);
  
  $WUtitle = preg_replace('|5|i',$ndays,$WUtitle,1);
  
  $doNumIcons = $maxIcons;
  if(count($WUforecasticons) < $maxIcons) { $doNumIcons = count($WUforecasticons); }

  $IncludeMode = false;
  $PrintMode = true;

  if (isset($doPrintWU) && ! $doPrintWU ) {
      print $Status;
      return;
  }
  if (isset($_REQUEST['inc']) && 
      strtolower($_REQUEST['inc']) == 'noprint' ) {
      print $Status;
	  return;
  }

if (isset($_REQUEST['inc']) && strtolower($_REQUEST['inc']) == 'y') {
  $IncludeMode = true;
}
if (isset($doIncludeWU)) {
  $IncludeMode = $doIncludeWU;
}

$printHeading = true;
$printIcons = true;
$printText = true;

if (isset($doPrintHeadingWU)) {
  $printHeading = $doPrintHeadingWU;
}
if (isset($_REQUEST['heading']) ) {
  $printHeading = substr(strtolower($_REQUEST['heading']),0,1) == 'y';
}

if (isset($doPrintIconsWU)) {
  $printIcons = $doPrintIconsWU;
}
if (isset($_REQUEST['icons']) ) {
  $printIcons = substr(strtolower($_REQUEST['icons']),0,1) == 'y';
}
if (isset($doPrintTextWU)) {
  $printText = $doPrintTextWU;
}
if (isset($_REQUEST['text']) ) {
  $printText = substr(strtolower($_REQUEST['text']),0,1) == 'y';
}


if (! $IncludeMode and $PrintMode) { ?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<title>WeatherUnderground <?php echo $WUtitle . ' - ' . $WUforecastcity; ?></title>
    <meta http-equiv="Content-Type" content="text/html; charset=<?php echo $charsetOutput; ?>" />
</head>
<body style="font-family:Verdana, Arial, Helvetica, sans-serif; font-size:12px; background-color:#FFFFFF">

<?php
} // end printmode and not includemode
//print $Status;
// if the forecast text is blank, prompt the visitor to force an update

if($UnSupported) {

  print <<< EONAG
<h1>Sorry.. this <a href="$WU_URL">forecast</a> can not be processed at this time.</h1>


EONAG
;
}

if (strlen($WUforecasttext[0])<2 and $PrintMode and ! $UnSupported ) {

  echo '<br/><br/>Forecast blank? <a href="' . $PHP_SELF . '?force=1">Force Update</a><br/><br/>';

} 
if ($PrintMode and ($printHeading or $printIcons)) {  ?>
  <table width="100%" style="border: none;" class="WUforecast">
  <?php echo $ddMenu ?>
    <?php if($printHeading) { ?>
    <tr align="center" style="background-color: #FFFFFF;">
      <td><b>WeatherUnderground <?php echo $WUtitle; ?>: </b><span style="color: green;">&nbsp;
	   <?php echo $WUforecastcity; ?></span>
      </td>
    </tr>
	<?php } // end print heading
	
	if ($printIcons) {
	?>
    <tr>
      <td align="center">
	    <table width="100%" border="0" cellpadding="0" cellspacing="0">  
	<?php
	  // see if we need to fold the icon rows due to long text length
	  $doFoldRow = false; // don't assume we have to fold the row..
	  if($foldIconRow) {
		  $iTitleLen =0;
		  $iTempLen = 0;
		  $iCondLen = 0;
		  for($i=0;$i<$doNumIcons;$i++) {
			$iTitleLen += strlen(strip_tags($WUforecasttitles[$i]));
			$iCondLen += strlen(strip_tags($WUforecastcond[$i]));
			$iTempLen += strlen(strip_tags($WUforecasttemp[$i]));  
		  }
		  print "<!-- lengths title=$iTitleLen cond=$iCondLen temps=$iTempLen -->\n";
		  $maxChars = 135;
		  if($iTitleLen >= $maxChars or 
		     $iCondLen >= $maxChars or
			 $iTempLen >= $maxChars ) {
				 print "<!-- folding icon row -->\n";
				 $doFoldRow = true;
			 } 
			 
	  }
	  $startIcon = 0;
	  $finIcon = $doNumIcons;
	  $incr = $doNumIcons;
	  if ($doFoldRow) { $wdth = $wdth*2; $incr = $numIconsInFoldedRow; }
  
	for ($k=$startIcon;$k<$doNumIcons-1;$k+=$incr) { // loop over icon rows, 5 at a time until done
	  $startIcon = $k;
	  if ($doFoldRow) { $finIcon = $startIcon+$numIconsInFoldedRow; } else { $finIcon = $doNumIcons; }
	  $finIcon = min($finIcon,$doNumIcons);
	  print "<!-- start=$startIcon fin=$finIcon num=$doNumIcons -->\n";
	  if(!$doRTL) {
        print "	      <tr valign=\"top\" align=\"center\">\n";
	  } else {
        print "	      <tr valign=\"top\" align=\"center\" style=\"direction: rtl\">\n";
	  }
	  
	  for ($i=$startIcon;$i<$finIcon;$i++) {
		$ni = $doRTL?$numIconsInFoldedRow-1-$i+$startIcon+$k:$i;  
	    print "<td style=\"width: $wdth%; text-align: center;\"><span style=\"font-size: 8pt;\">$WUforecasttitles[$ni]</span></td>\n";
		
	  }
	
print "          </tr>\n";	
	  if(!$doRTL) {
        print "	      <tr valign=\"top\" align=\"center\">\n";
	  } else {
        print "	      <tr valign=\"top\" align=\"center\" style=\"direction: rtl\">\n";
	  }
	
	  for ($i=$startIcon;$i<$finIcon;$i++) {
		$ni = $doRTL?$numIconsInFoldedRow-1-$i+$startIcon+$k:$i;  
	    print "<td style=\"width: $wdth%;\">" . WU_img_replace($WUforecasticon[$ni],$WUforecastcond[$ni],$WUforecastpop[$ni]) . "</td>\n";
	  }
	?>
          </tr>	
	      <tr valign ="top" align="center">
	<?php
	  for ($i=$startIcon;$i<$finIcon;$i++) {
		$ni = $doRTL?$numIconsInFoldedRow-1-$i+$startIcon+$k:$i;  

	    print "<td style=\"width: $wdth%; text-align: center;\"><span style=\"font-size: 8pt;\">$WUforecastcond[$ni]</span></td>\n";
	  }
	
      print "	      </tr>\n";	
	  if(!$doRTL) {
        print "	      <tr valign=\"top\" align=\"center\">\n";
	  } else {
        print "	      <tr valign=\"top\" align=\"center\" style=\"direction: rtl\">\n";
	  }
	  
	  for ($i=$startIcon;$i<$finIcon;$i++) {
		$ni = $doRTL?$numIconsInFoldedRow-1-$i+$startIcon+$k:$i;  
	    print "<td style=\"width: $wdth%; text-align: center;\">$WUforecasttemp[$ni]</td>\n";
	  }
	  ?>
          </tr>
	<?php if(! $iconDir) { // print a PoP row since they aren't using icons 
	  if(!$doRTL) {
        print "	      <tr valign=\"top\" align=\"center\">\n";
	  } else {
        print "	      <tr valign=\"top\" align=\"center\" style=\"direction: rtl\">\n";
	  }
	
	  for ($i=$startIcon;$i<$finIcon;$i++) {
		$ni = $doRTL?$numIconsInFoldedRow-1-$i+$startIcon+$k:$i;  
	    print "<td style=\"width: $wdth%; text-align: center;\">";
	    if($WUforecastpop[$ni] > 0) {
  		  print "<span style=\"font-size: 8pt; color: #009900;\">PoP: $WUforecastpop[$ni]%</span>";
		} else {
		  print "&nbsp;";
		}
		print "</td>\n";
		
	  }
	?>
          </tr>	
	  <?php } // end if iconDir ?>
      <?php if ($doFoldRow) { 
	  if(!$doRTL) {
        print "	      <tr valign=\"top\" align=\"center\">\n";
	  } else {
        print "	      <tr valign=\"top\" align=\"center\" style=\"direction: rtl\">\n";
	  }
	  
	    for ($i=$startIcon;$i<$finIcon;$i++) {
	      print "<td style=\"width: $wdth%; text-align: center;\">&nbsp;</td>\n";
      
	    }
		print "</tr>\n";
      } // end doFoldRow ?>
  <?php } // end of foldIcon loop ?>
        </table><!-- end icon table -->
     </td>
   </tr><!-- end print icons -->
   	<?php } // end print icons ?>
</table>
  <p>&nbsp;</p>
<?php } // end print header or icons

if ($PrintMode and $printText) { ?>

<table style="border: 0" width="100%" class="WUforecast">
	<?php
	  for ($i=0;$i<count($WUforecasttitles);$i++) {
        print "<tr valign =\"top\" align=\"left\">\n";
		if(!$doRTL) { // normal Left-to-right
	      print "<td style=\"width: 20%;\"><b>$WUforecasttitles[$i]</b><br />&nbsp;<br /></td>\n";
	      print "<td style=\"width: 80%;\">$WUforecasttext[$i]</td>\n";
		} else { // print RTL format
	      print "<td style=\"width: 80%; text-align: right;\">$WUforecasttext[$i]</td>\n";
	      print "<td style=\"width: 20%; text-align: right;\"><b>$WUforecasttitles[$i]</b><br />&nbsp;<br /></td>\n";
		}
		print "</tr>\n";
	  }
	?>
   </table>
<?php } // end print text ?>
<?php if ($PrintMode) { ?>
<p>&nbsp;</p>
<p>Forecast from <a href="<?php echo htmlspecialchars($fileName); ?>">WeatherUnderground</a> 
for <?php echo $WUforecastcity; ?>.
<?php if($iconType <> '.jpg') {
	print "<br/>Animated forecast icons courtesy of <a href=\"http://www.meteotreviglio.com/\">www.meteotreviglio.com</a>.";
} 
?>
</p>
<?php
} // end printmode

 if (! $IncludeMode and $PrintMode ) { ?>
</body>
</html>
<?php 
}  

 
// Functions --------------------------------------------------------------------------------

function WU_fetchUrlWithoutHanging($url,$cacheurl)
   {
   global $Status;
   // Set maximum number of seconds (can have floating-point) to wait for feed before displaying page without feed
   $numberOfSeconds=4;    

   // Suppress error reporting so Web site visitors are unaware if the feed fails
   error_reporting(0);

   // Extract resource path and domain from URL ready for fsockopen

   $url = str_replace("http://","",$url);
   $urlComponents = explode("/",$url);
   $domain = $urlComponents[0];
   $resourcePath = str_replace($domain,"",$url);
   $xml = '';

   // Establish a connection
   $socketConnection = fsockopen($domain, 80, $errno, $errstr, $numberOfSeconds);

   if (!$socketConnection)
       {

       // You may wish to remove the following debugging line on a live Web site

       $Status .= "<!-- Network error: $errstr ($errno) -->\n";
       }    // end if
   else    {
       $xml = '';
       fputs($socketConnection, "GET $resourcePath HTTP/1.1\r\nHost: $domain\r\nConnection: Close\r\nCookie: Units=metric;\r\nUser-agent: PHP,WU-forecast.php,saratoga-weather.org\r\n\r\n");
   
       // Loop until end of file
       while (!feof($socketConnection))
           {
           $xml .= fgets($socketConnection, 4096);
           }    // end while

       fclose ($socketConnection);

       }    // end else

   $xml = preg_replace('|\r\n2000\r\n|is','',$xml);  // this funky string started appearing in WU website

   return($xml);

   }    // end function

// -------------------------------------------------------------------------------------------
   
 function WU_img_replace ( $WUimage, $WUcondtext,$WUpop) {
//
// optionally replace the WeatherUnderground icon with an NWS icon instead.
// 
 global $NWSiconlist,$iconDir,$iconType,$Status;
// $WU_URL = 'http://icons-aa.wxug.com/graphics/conds/';
// $WU_URL = 'http://icons.wunderground.com/graphics/conds/2005/';
 $WUiconURL = 'http://icons-pe.wxug.com/i/c/50/';
 
 $curicon = isset($NWSiconlist[$WUimage][0])?$NWSiconlist[$WUimage][0]:''; // translated icon (if any)

 if (!$iconDir or !$curicon) { // no change.. use WU icon
   return("<img src=\"$WUiconURL$WUimage\" width=\"50\" height=\"50\" 
  alt=\"$WUcondtext\" title=\"$WUcondtext\"/>"); 
 }
  if($iconType <> '.jpg') {
	  $curicon = preg_replace('|\.jpg|',$iconType,$curicon);
  }
  $Status .= "<!-- replace icon '$WUimage' with ";
  if ($WUpop > 0) {
	$testicon = preg_replace('|'.$iconType.'|',$WUpop.$iconType,$curicon);
	if (file_exists("$iconDir$testicon")) {
	  $newicon = $testicon;
	} else {
	  $newicon = $curicon;
	}
  } else {
	$newicon = $curicon;
  }
  $Status .= "'$newicon' pop=$WUpop -->\n";

  return("<img src=\"$iconDir$newicon\" width=\"55\" height=\"58\" 
  alt=\"$WUcondtext\" title=\"$WUcondtext\"/>"); 
 
 
 }

// -------------------------------------------------------------------------------------------
 
function WU_prepareJSON($input) {
	global $Status;
   
   //This will convert ASCII/ISO-8859-1 to UTF-8.
   //Be careful with the third parameter (encoding detect list), because
   //if set wrong, some input encodings will get garbled (including UTF-8!)

   list($isUTF8,$offset,$msg) = WU_check_utf8($input);
   
   if(!$isUTF8) {
	   $Status .= "<!-- WU_prepareJSON: Oops, non UTF-8 char detected at $offset. $msg. Doing utf8_encode() -->\n";
	   $str = utf8_encode($input);
       list($isUTF8,$offset,$msg) = WU_check_utf8($str);
	   $Status .= "<!-- WU_prepareJSON: after utf8_encode, i=$offset. $msg. -->\n";   
   } else {
	   $Status .= "<!-- WU_prepareJSON: $msg. -->\n";
	   $str = $input;
   }
  
   //Remove UTF-8 BOM if present, json_decode() does not like it.
   if(substr($str, 0, 3) == pack("CCC", 0xEF, 0xBB, 0xBF)) $str = substr($str, 3);
   
   return $str;
}

// -------------------------------------------------------------------------------------------

function WU_check_utf8($str) {
// check all the characters for UTF-8 compliance so json_decode() won't choke
// Sometimes, an ISO international character slips in the WU text string.	  
     $len = strlen($str); 
     for($i = 0; $i < $len; $i++){ 
         $c = ord($str[$i]); 
         if ($c > 128) { 
             if (($c > 247)) return array(false,$i,"c>247 c='$c'"); 
             elseif ($c > 239) $bytes = 4; 
             elseif ($c > 223) $bytes = 3; 
             elseif ($c > 191) $bytes = 2; 
             else return false; 
             if (($i + $bytes) > $len) return array(false,$i,"i+bytes>len bytes=$bytes,len=$len"); 
             while ($bytes > 1) { 
                 $i++; 
                 $b = ord($str[$i]); 
                 if ($b < 128 || $b > 191) return array(false,$i,"128<b or b>191 b=$b"); 
                 $bytes--; 
             } 
         } 
     } 
     return array(true,$i,"Success. Valid UTF-8"); 
 } // end of check_utf8

// -------------------------------------------------------------------------------------------
 
function WU_decode_JSON_error() {
	
  $Status = '';
  $Status .= "<!-- json_decode returns ";
  switch (json_last_error()) {
	case JSON_ERROR_NONE:
		$Status .= ' - No errors';
	break;
	case JSON_ERROR_DEPTH:
		$Status .= ' - Maximum stack depth exceeded';
	break;
	case JSON_ERROR_STATE_MISMATCH:
		$Status .= ' - Underflow or the modes mismatch';
	break;
	case JSON_ERROR_CTRL_CHAR:
		$Status .= ' - Unexpected control character found';
	break;
	case JSON_ERROR_SYNTAX:
		$Status .= ' - Syntax error, malformed JSON';
	break;
	case JSON_ERROR_UTF8:
		$Status .= ' - Malformed UTF-8 characters, possibly incorrectly encoded';
	break;
	default:
		$Status .= ' - Unknown error, json_last_error() returns \''.json_last_error(). "'";
	break;
   } 
   $Status .= " -->\n";
   return($Status);
}

// -------------------------------------------------------------------------------------------

function WU_get_APIURL ($rawURL) {
	global $WUAPIkey,$WULANG,$Status,$doDebug;

// try to generate an API request URL from a WU page URL	
/*
'Saratoga|http://www.wunderground.com/cgi-bin/findweather/getForecast?query=95070',
'Aarhus|http://www.wunderground.com/global/stations/06075.html',
'Auckland|http://english.wunderground.com/cgi-bin/findweather/getForecast?query=-36.910%2C174.771&sp=IAUCKLAN110', // Awhitu, Waiuku New Zealand
'Amsterdam|http://www.wunderground.com/cgi-bin/findweather/getForecast?query=Amsterdam%2C+Netherlands',
'Paris|http://www.wunderground.com/cgi-bin/findweather/getForecast?query=Paris%2C+France',
'Stockholm|http://www.wunderground.com/cgi-bin/findweather/getForecast?query=Stockholm%2C+Sweden',
'Oslo|http://www.wunderground.com/cgi-bin/findweather/getForecast?query=Oslo%2C+Norway',
'Moscow|http://www.wunderground.com/global/stations/27612.html',
'Athens|http://www.wunderground.com/cgi-bin/findweather/getForecast?query=Athens%2C+Greece',
'Tel Aviv|http://www.wunderground.com/cgi-bin/findweather/getForecast?query=Tel+Aviv%2C+Israel',
'Madrid|http://www.wunderground.com/cgi-bin/findweather/getForecast?query=Madrid%2C+Spain',
'Helsinki|http://www.wunderground.com/cgi-bin/findweather/getForecast?query=Helsinki%2C+Finland',
'Castrop-Rauxel|http://www.wunderground.com/cgi-bin/findweather/getForecast?query=51.572%2C7.376&sp=INORDRHE72',
'Southampton|http://www.wunderground.com/global/stations/03865.html',
'Canvey Island, Essex|http://www.wunderground.com/weather-forecast/zmw:00000.57.03691',
'Saratoga PWS|http://www.wunderground.com/cgi-bin/findweather/getForecast?query=pws:KCASARAT1',
'St. Nicholas|http://www.wunderground.com/q/locid:UKEN1390',
'Alberta (Canada)|http://www.wunderground.com/q/locid:CAXX4520',
'Andover (Middle Wallop)|http://www.wunderground.com/cgi-bin/findweather/getForecast?query=zmw:00000.1.03749',
'Assen (Holland)|http://www.wunderground.com/q/zmw:00000.6.06280',
'Honolulu|http://www.wunderground.com/US/HI/Honolulu.html',
'Malta|http://www.wunderground.com/global/ML.html',

as:

http://api.wunderground.com/api/$WUAPIkey/forecast10day/geolookup/lang:$WULANG/q/$WUQUERY.json

// Note: new formats for the query:
//  CA/San_Francisco	US state/city
//  60290	US zipcode
//  Australia/Sydney	country/city
//  37.8,-122.4	latitude,longitude
//  KJFK	airport code
//  pws:KCASANFR70	PWS id

*/
   $newURL = 'http://api.wunderground.com/api/%s/forecast10day/geolookup/lang:%s/q/%s.json';

   $Status .= "<!-- WU_API Raw URL='$rawURL' -->\n";
   if(preg_match("|query=([^\&]+)|i",$rawURL,$matches)) {
	 $rawQuery = urldecode(trim($matches[1]));
	 
	 if(preg_match('|^[\d\-\.\,]+$|',$rawQuery)) { // likely lat,long query.. use it
	 
	 } else { // likely a City, State query
		$t = explode(', ',$rawQuery);
		if(isset($t[1])) { $rawQuery = $t[1].'/'.$t[0]; }
		$rawQuery = preg_replace('| |','_',$rawQuery);
	 }
	 if($doDebug) {$Status .= "<!-- query='$rawQuery' -->\n"; }
	 $newURL = sprintf($newURL,$WUAPIkey,$WULANG,$rawQuery);
     $Status .= "<!-- WU API New URL='$newURL' -->\n";
	 return($newURL);
   } // end query= processing
   
   if(preg_match('|global/stations/(\d+).html|i',$rawURL,$matches)) {
	 $rawQuery = 'zmw:00000.1.'.trim($matches[1]);
	 $newURL = sprintf($newURL,$WUAPIkey,$WULANG,$rawQuery);
     $Status .= "<!-- WU API New URL='$newURL' -->\n";
	 return($newURL);
   }
   
   if(preg_match('|weather-forecast/zmw:([\d\.]+)|i',$rawURL,$matches)) {
	 $rawQuery = 'zmw:'.trim($matches[1]);
	 $newURL = sprintf($newURL,$WUAPIkey,$WULANG,$rawQuery);
     $Status .= "<!-- WU API New URL='$newURL' -->\n";
	 return($newURL);
   }
   
   if(preg_match('|/q/([^\s]+)|i',$rawURL,$matches)) { // handle alternate locid:, zmw: 
	 $rawQuery = trim($matches[1]);
	 $newURL = sprintf($newURL,$WUAPIkey,$WULANG,$rawQuery);
     $Status .= "<!-- WU API New URL='$newURL' -->\n";
	 return($newURL);
   }

   if(preg_match('|/US/(.*)$|i',$rawURL,$matches)) { // handle US ST/Cityname
	 $rawQuery = trim($matches[1]);
	 $newURL = sprintf($newURL,$WUAPIkey,$WULANG,$rawQuery);
     $Status .= "<!-- WU API New URL='$newURL' -->\n";
	 return($newURL);
   }

   if(preg_match('|/global/([^\s]+)\.html|i',$rawURL,$matches)) { // handle US ST/Cityname
	 $rawQuery = trim($matches[1]);
	 $newURL = sprintf($newURL,$WUAPIkey,$WULANG,$rawQuery);
     $Status .= "<!-- WU API New URL='$newURL' -->\n";
	 return($newURL);
   }
   
   return('');
	
}

function WU_loadLangDefaults () {
	global $WUlanguages, $WUlangCharsets;
/*

WU Language definitions for Lang: in API URL
"AF" = Afrikaans
"AL" = Albanian
"AR" = Arabic
"HY" = Armenian
"AZ" = Azerbaijani
"EU" = Basque
"BY" = Belarusian
"BU" = Bulgarian
"LI" = British English
"MY" = Burmese
"CA" = Catalan
"CN" = Chinese - Simplified
"TW" = Chinese - Traditional
"CR" = Croatian
"CZ" = Czech
"DK" = Danish
"DV" = Dhivehi
"NL" = Dutch
"EN" = English
"EO" = Esperanto
"ET" = Estonian
"FA" = Farsi
"FI" = Finnish
"FR" = French
"FC" = French Canadian
"GZ" = Galician
"DL" = German
"KA" = Georgian
"GR" = Greek
"GU" = Gujarati
"HT" = Haitian Creole
"IL" = Hebrew
"HI" = Hindi
"HU" = Hungarian
"IS" = Icelandic
"IO" = Ido
"ID" = Indonesian
"IR" = Irish Gaelic
"IT" = Italian
"JP" = Japanese
"JW" = Javanese
"KM" = Khmer
"KR" = Korean
"KU" = Kurdish
"LA" = Latin
"LV" = Latvian
"LT" = Lithuanian
"ND" = Low German
"MK" = Macedonian
"MT" = Maltese
"GM" = Mandinka
"MI" = Maori
"MR" = Marathi
"MN" = Mongolian
"NO" = Norwegian
"OC" = Occitan
"PS" = Pashto
"GN" = Plautdietsch
"PL" = Polish
"BR" = Portuguese
"PA" = Punjabi
"RO" = Romanian
"RU" = Russian
"SR" = Serbian
"SK" = Slovak
"SL" = Slovenian
"SP" = Spanish
"SI" = Swahili
"SW" = Swedish
"CH" = Swiss
"TL" = Tagalog
"TT" = Tatarish
"TH" = Thai
"TR" = Turkish
"TK" = Turkmen
"UA" = Ukrainian
"UZ" = Uzbek
"VU" = Vietnamese
"CY" = Welsh
"SN" = Wolof
"JI" = Yiddish - transliterated
"YI" = Yiddish - unicode
*/
 
 $WUlanguages = array(  // our template language codes v.s. lang:LL codes for JSON
	'af' => 'AF',
	'bg' => 'BU',
	'ct' => 'CA',
	'dk' => 'DK',
	'nl' => 'NL',
	'en' => 'EN',
	'fi' => 'FI',
	'fr' => 'FR',
	'de' => 'DL',
	'el' => 'GR',
	'ga' => 'IR',
	'it' => 'IT',
	'he' => 'IL',
	'hu' => 'HU',
	'no' => 'NO',
	'pl' => 'PL',
	'pt' => 'BR',
	'ro' => 'RO',
	'es' => 'SP',
	'se' => 'SW',
	'si' => 'SL',
  );

  $WUlangCharsets = array(
	'bg' => 'ISO-8859-5',
	'el' => 'ISO-8859-7',
	'he' => 'UTF-8', 
	'hu' => 'ISO-8859-2',
	'ro' => 'ISO-8859-2',
	'pl' => 'ISO-8859-2',
	'si' => 'ISO-8859-2',
	'ru' => 'ISO-8859-5'
  );

} // end loadLangDefaults


// End of functions --------------------------------------------------------------------------

?>


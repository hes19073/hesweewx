/* javascript for the weex skin                     */
/* copyright 2014                                   */
/* $Id: hesweewx.js 666 2014-02-07 14:14:38Z hes  $ */
/* allgemeine Funktionen für die Navigation         */


function openURL(urlname)
      {
   window.location=urlname;
}

function openNoaaFile(date)
      {
        var url = "NOAA/NOAA-";
        url = url + date;
        url = url + ".txt";
        window.location=url;
}

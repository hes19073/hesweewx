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

function openArchivFile(date)
      {
        var url = "Archiv/KR-";
        url = url + date;
        url = url + "-table.html";
        window.location=url;
}

var wxpopup;
var wxpopupT = 16;
var wxpopupL = 20;
var wxpopupclass = 'popup';

function showGraphPopup(elem) {
    if(!elem.href) return;
    if(wxpopup == null) {
        wxpopup = document.createElement('div');
        wxpopup.style.position = 'absolute';
        wxpopup.style.filter='alpha(opacity=90)';
        wxpopup.style.opacity='0.90';
        popupanchor = document.getElementById('popupanchor');
        if(!popupanchor) {
            popupanchor = document.body;
        }
        popupanchor.appendChild(wxpopup);
    }
/*
    var coord = findPos(elem);
    wxpopup.style.top = coord.top + wxpopupT;
    wxpopup.style.left = coord.left + wxpopupL;
*/
    var html = "<div id='graphPopup'>";
    html += "<img src='" + elem.href + "' alt='graph'>";
    html += "</div>";
    wxpopup.innerHTML = html;
    wxpopup.style.visibility = 'visible';
}

function hideGraphPopup() {
    if(wxpopup != null) {
        wxpopup.style.visibility = 'hidden';
    }
}

function findPos(elem) {
    var top = 0;
    var left = 0;
    if(elem.offsetParent) {
        do {
            top += elem.offsetTop;
            left += elem.offsetLeft;
        } while((elem=elem.offsetParent) != null);
    }
    var coord = new Object();
    coord.top = top;
    coord.left = left;
    return coord;
}

function applypopups() {
    var anchors = document.getElementsByTagName('a');
    for(var i=0; i<anchors.length; i++) {
        if(anchors[i].className.match(wxpopupclass)) {
            setOnMouseOver(anchors[i]);
            setOnMouseOut(anchors[i]);
        }
    }
}
    
// closure ensures correct element
function setOnMouseOver(elem) {
    elem.onmouseover = function() { showGraphPopup(elem); }
}

function setOnMouseOut(elem) {
    elem.onmouseout = function() { hideGraphPopup(); }
}

function toggle(control, id) {
  elem = document.getElementById(id + '.hours');
  if(elem) {
    if(elem.style.display != 'none') {
      elem.style.display = 'none';
      control.src = 'xicons/triangle-right.png'
    } else {
      elem.style.display = 'inline';
      control.src = 'xicons/triangle-down.png'
    }
  }
}

// When the user clicks on <div>, open the popup
function myFunction() {
    var popup = document.getElementById("myPopup");
    popup.classList.toggle("show");
}

function myFunction2() {
    var popup = document.getElementById("myPopup1");
    popup.classList.toggle("show");
}

function myFunction2() {
    var popup = document.getElementById("myPopup2");
    popup.classList.toggle("show");
}

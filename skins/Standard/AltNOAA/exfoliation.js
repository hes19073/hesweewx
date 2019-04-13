// javascript for exfoliation-for-weewx
// $Id$
// Copyright 2013 Matthew Wall
// This skin can be copied, modified, and distributed as long as this notice
// is included in any derivative work.

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

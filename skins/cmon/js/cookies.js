// javascript for cookies
// $Id: mitna.js 877 2014-03-10 19:34:17Z mwall $
// Copyright 2016 Matthew Wall

function set_cookie(name, value, dur) {
  if(dur==null || dur==0) dur=30;
  var today = new Date();
  var expire = new Date();
  expire.setTime(today.getTime() + 24*3600000*dur);
  document.cookie = name+"="+escape(value)+";expires="+expire.toGMTString();
}

function get_cookie(name, default_value) {
  if(name=="") return default_value;
  var cookie = " "+document.cookie;
  var i = cookie.indexOf(" "+name+"=");
  if(i<0) i = cookie.indexOf(";"+name+"=");
  if(i<0) return default_value;
  var j = cookie.indexOf(";", i+1);
  if(j<0) j = cookie.length;
  return unescape(cookie.substring(i + name.length + 2, j));
}


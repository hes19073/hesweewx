## weewx-footer-cookie for weewx - Copyright 2013-2014 Hartmut Schweidler
##  cookie.inc 634 2018-06-16 08:34:04Z hes1 $
## nach Vorlage von mwall $
#encoding UTF-8

<style> <!-- id cookie -->

#cookiedingsbums a {color:#000; text-decoration:none;}

#cookiedingsbums a:hover {text-decoration:underline;}

#cookiedingsbums div {padding:10px; padding-right:40px;}

#cookiedingsbums { 
   outline: 1px solid #7b92a9; 
   text-align:right; 
   border-top:1px solid #fff;
   background: #d6e0eb; 
   background: -moz-linear-gradient(top, #d6e0eb 0%, #f2f6f9 100%); 
   background: -webkit-gradient(linear, left top, left bottom, color-stop(0%,#d6e0eb), color-stop(100%,#f2f6f9)); 
   background: -webkit-linear-gradient(top, #d6e0eb 0%,#f2f6f9 100%); 
   background: -o-linear-gradient(top, #d6e0eb 0%,#f2f6f9 100%);
   background: -ms-linear-gradient(top, #d6e0eb 0%,#f2f6f9 100%); 
   background: linear-gradient(to bottom, #d6e0eb 0%,#f2f6f9 100%); 
   filter: progid:DXImageTransform.Microsoft.gradient(   startColorstr='#d6e0eb', endColorstr='#f2f6f9',GradientType=0 ); 
   position:fixed;
   bottom:0px; 
   z-index:10000; 
   width:100%; 
   font-size:12px; 
   line-height:16px;}

#cookiedingsbumsCloser {
   color: #777;
   font: 14px/100% arial, sans-serif;
   position: absolute;
   right: 5px;
   text-decoration: none;
   text-shadow: 0 1px 0 #fff;
   top: 5px;
   cursor:pointer;
   border-top:1px solid white; 
   border-left:1px solid white; 
   border-bottom:1px solid #7b92a9; 
   border-right:1px solid #7b92a9; 
   padding:4px;
   background: #ced6df; /* Old browsers */
   background: -moz-linear-gradient(top, #ced6df0%, #f2f6f9 100%); 
   background: -webkit-gradient(linear, left top, left bottom, color-stop(0%,#ced6df), color-stop(100%,#f2f6f9)); 
   background: -webkit-linear-gradient(top, #ced6df0%,#f2f6f9 100%); 
   background: -o-linear-gradient(top, #ced6df0%,#f2f6f9 100%); 
   background: -ms-linear-gradient(top, #ced6df0%,#f2f6f9 100%); 
   background: linear-gradient(to bottom, #ced6df0%,#f2f6f9 100%); 
   filter: progid:DXImageTransform.Microsoft.gradient(    startColorstr='#ced6df', endColorstr='#f2f6f9',GradientType=0 ); 
 }

#cookiedingsbumsCloser:hover {border-bottom:1px solid white; border-right:1px solid white; border-top:1px solid #7b92a9; border-left:1px solid #7b92a9;}

</style>

<div id="cookiedingsbums">
  <div>
   <span>Ja, auch diese Webseite verwendet Cookies. </span>
   <a href="http://blog.hes61.de/datenschutz">Hier erfahrt ihr alles zum Datenschutz</a>
  </div>
  <span id="cookiedingsbumsCloser" onclick="document.cookie = 'hidecookiedingsbums=1;path=/';jQuery('#cookiedingsbums').slideUp()">&#10006;</span>
</div>

<script>

if(document.cookie.indexOf('hidecookiedingsbums=1') != -1){
jQuery('#cookiedingsbums').hide();
}
else{
jQuery('#cookiedingsbums').prependTo('body');
jQuery('#cookiedingsbumsCloser').show();
}

</script>


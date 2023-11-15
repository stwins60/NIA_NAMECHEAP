
function myMap() {
  var latlng = new google.maps.LatLng(41.952820,-87.653084);
  var latlng2 = new google.maps.LatLng(41.952820,-87.653084);
  var myOptions = {
    zoom: 12,
    center: latlng
  };
  var map = new google.maps.Map(document.getElementById("contact-map"), myOptions);
  var myMarker = new google.maps.Marker({
    position: latlng,
    map: map,
    title:"United States"
  });

}
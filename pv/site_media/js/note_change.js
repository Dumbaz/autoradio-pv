django.jQuery(document).ready( function() {

   /* Get the already saved timeslot_id to preserve if past */
   var selected_timeslot_id = django.jQuery('select#id_timeslot option:selected').val() || 0;
   var selected_timeslot_val = django.jQuery('select#id_timeslot option:selected').text() || ''

	/* If a show is selected load its timeslots into the corresponding select */
	django.jQuery("select#id_show").on("change", function() {

	   /* Get selected show */
	   var show_id = django.jQuery("select#id_show option:selected").val();
	   if( show_id == '' ) {
	      django.jQuery('select#id_timeslot').html( new Option( '', '' ) );
	      return;
	   }

	   django.jQuery('select#id_timeslot').fadeOut();

	   /* Call ajax function and retrieve array containing objects */
	   django.jQuery.ajax({
            url: '/api/v1/timeslots/',
            type: 'GET',
            data: {
              'show_id': show_id,
              'csrfmiddlewaretoken': django.jQuery('input[name="csrfmiddlewartetoken"]').val()
            },
            success: function(timeslots) {
	            /* Populate timeslot select */
	            var options = new Array();
	            i = 0;

	            // Preserve an already selected timeslot
	            if( selected_timeslot_id > 0 ) {
	            	options[0] = new Option( selected_timeslot_val, selected_timeslot_id );
	            	i = 1;
	            }

	            for( var i=i; i < timeslots.length; i++ ) {
	               options[i] = new Option( moment.utc( timeslots[i].start ).format('dd, D.M. YYYY HH:mm') + ' - ' + moment.utc( timeslots[i].end ).format('HH:mm'), parseInt(timeslots[i].id) );
	            }

	            django.jQuery('select#id_timeslot').html( options ).fadeIn();

	         },
	         error: function() {
	            alert("Couldn't load timeslots.");
	         }

		});

   });

});
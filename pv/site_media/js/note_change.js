django.jQuery(document).ready( function() {

   /* Get the already saved timeslot_id to preserve if past */
   var selected_timeslot_id = django.jQuery('select#id_timeslot option:selected').val() || 0;

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
            url: '/export/get_timeslots_by_show',
            type: 'GET',
            data: {
              'show_id': show_id,
              'timeslot_id': selected_timeslot_id,
              'csrfmiddlewaretoken': django.jQuery('input[name="csrfmiddlewartetoken"]').val()
            },
            success: function(timeslots) {
	            /* Populate timeslot select */
	            var options = new Array();

	            for( var i=0; i < timeslots.length; i++ ) {
	               options[i] = new Option( timeslots[i].timeslot, parseInt(timeslots[i].timeslot_id) ); //+ " " + moment.utc( timeslots[i].start ).format('dddd, D.M. YYYY HH:mm') + ' - ' + moment.utc( timeslots[i].end ).format('HH:mm'), timeslots[i].timeslot_id );
	            }

	            django.jQuery('select#id_timeslot').html( options ).fadeIn();

	         },
	         error: function() {
	            alert("Couldn't load timeslots.");
	         }

		});

   });

});
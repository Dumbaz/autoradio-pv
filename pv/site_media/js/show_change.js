/* Toggle visibility of weekday/until-selects dependent on the selected rrule */
function toggleSelects( select_elm ) {

   var id = select_elm.closest('tr').attr('id'); // ID of programslot
   var option_val = parseInt( django.jQuery('#' + select_elm.attr('id') + ' option:selected').val() ); // Selected option value
   var weekday_select = django.jQuery('#id_' + id + '-byweekday'); // Target weekday-<select> to show/hide
   var until_select = django.jQuery('#id_' + id + '-until'); // Target until-<select> to show/hide
   var dstart = django.jQuery('#id_' + id + '-dstart'); // dstart value to copy to end date

   if( option_val == NaN )
     return;

   // 1 = once, 2 = daily, 3 = business days
   if( option_val < 4 ) {
      weekday_select.fadeOut().val(0); // Although it'll be ignored, select Monday in order the form can be validated

      if( option_val == 1 ) {
         // If once, hide the until-date too and try to set it to dstart
			if( until_select.val() == '')
			  until_select.val(dstart.val());

         until_select.fadeOut().next('.datetimeshortcuts').fadeOut();
      } else {
         until_select.fadeIn().next('.datetimeshortcuts').fadeIn();
      }


   } else {
      weekday_select.fadeIn();
      until_select.fadeIn().next('.datetimeshortcuts').fadeIn();
   }

}


django.jQuery(document).ready( function() {

   moment.locale("de");

 	/* Toggle selects dependent on rrule option on load */
   django.jQuery(".field-rrule select").each( function(i) {
      toggleSelects( django.jQuery(this) );
   });

   /* ...and on change */
   django.jQuery(document).on('change', '.field-rrule select', function() {
      toggleSelects( django.jQuery(this) )
   });


   django.jQuery(document).on('blur', '.field-dstart input', function() {
		var ps_id = django.jQuery(this).closest('tr').attr("id");
      var dstart = django.jQuery(this).val();

      //django.jQuery(this).removeClass('validation-error');

   	/* Set the until date to dstart if editing a programslot with freq 'once' */
		if( django.jQuery('#id_' + ps_id + '-rrule option:selected').val() == 1 ) {
   		django.jQuery('#id_' + ps_id + '-until').show().val(dstart).hide();
   	}

		/* Check if dstart is not in the past */
      /*
      if( dstart != '' ) {
        console.log(moment(dstart, "DD.MM.YYYY").unix());
        console.log(moment().unix());

        if( moment(dstart, "DD.MM.YYYY").unix() <= moment().unix() ) {
            alert('Startdatum darf nicht in der Vergangenheit liegen');
            django.jQuery(this).addClass('validation-error');
        }

      }
      */

   });


   django.jQuery(document).on('submit', '#show_form', function(e) {
       django.jQuery('input').removeClass('validation-error');

       django.jQuery('.field-until input').each( function() {

           var until = django.jQuery(this).val();
           var dstart = django.jQuery(this).closest('tr').find('.field-dstart input').val();
           var until_timestamp =  moment(until, "DD.MM.YYYY") / 1000;
           var dstart_timestamp = moment(dstart, "DD.MM.YYYY") / 1000;

           if( until != '' && dstart != '') {
               if( until_timestamp <= dstart_timestamp ) {
                   e.preventDefault();
                   alert('Enddatum darf nicht vor dem Startdatum liegen');
                   django.jQuery(this).addClass('validation-error');
               }

           } else if( until == '' && dstart != '') {
               e.preventDefault();
               alert('Enddatum darf nicht leer sein');
               django.jQuery(this).addClass('validation-error');
           } else if( dstart == '' && until != '') {
           	   e.preventDefault();
           	   alert('Startdatum darf nicht leer sein');
               django.jQuery(this).closest('tr').find('.field-dstart input').addClass('validation-error');
           } else {
               return;
           }

       });


   });

});
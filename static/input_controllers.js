var input_controllers = function() {
     $cities = $('#cities');
     $cities.prepend('<option value="" selected>Wybierz miasto</option>');

    $clinics = $('#clinics');
    $services = $('#services');

    var cities_change_fn = function() {
        var cityId = $(':selected', this)[0].value;

         $.get( "/clinics/" + cityId).done(function( data ) {
            $clinics.empty()
            $services.empty()
            keys = Object.keys(data);
            if(keys.length > 1) {
               $clinics.append('<option value="-1"> Dowolna </option>');
               keys.forEach(function(k) {
                    $clinics.append(`<option value="${k}"> ${data[k]} </option>`);
               })
            } else if (keys.length == 1) {
                 id = keys[0]
                 $clinics.append(`<option value="${id}" selected> ${data[id]} </option>`);
                 clinics_change_fn()
            }
            $clinics.selectpicker('refresh');
            $services.selectpicker('refresh');
        });
    }

    var selectedClinics = [];

    var clinics_change_fn = function(e, params) {

        var city_id = $cities.find(":selected")[0].value;
        $selected = $(':selected', this);

        var newValues = $($(this).val()).not(selectedClinics).get();

        if(newValues[0] == -1 && $selected.length > 1) {
            $clinics.selectpicker('deselectAll')
            $clinics.selectpicker('val', '-1');
            $clinics.selectpicker('refresh');
        } else if (newValues[0] != -1 && selectedClinics.includes("-1")) {
            $clinics.selectpicker('deselectAll')
            $clinics.selectpicker('val', newValues[0]);
            $clinics.selectpicker('refresh');
        }
        selectedClinics = $(this).val();

        var clinic_ids = $.map($selected, function(option) {
         return option.value;
        });

        if(clinic_ids.length == 1 && clinic_ids[0] == -1) {
            clinic_ids = [];
        }
        var body = { city_id: city_id, clinic_ids: clinic_ids }

        $.post( "/services", body).done(function(data) {
            $services.empty()
            $services.append('<option value="">Wybierz usługę</option>');
            Object.keys(data).forEach(function(k) {
               $services.append(`<option value="${k}"> ${data[k]} </option>`);
            })
            $services.selectpicker('refresh');
        });
    };

    $cities.on('change', cities_change_fn);
    $clinics.on('change', clinics_change_fn);
}

$(function() {

   input_controllers();
   //time_controllers();
   date_controllers();

});


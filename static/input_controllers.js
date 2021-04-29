var input_controllers = function() {
     $cities = $('#cities');
     $cities.prepend('<option value="" selected>Wybierz miasto</option>');

    $clinics = $('#clinics');
    $services = $('#services');
    $referral_id = $('#referral_id')
    $doctors = $('#doctors');
    selectedClinics = [], selectedDoctors = [];

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
                 $clinics.change()
            }
            $clinics.selectpicker('refresh');
            $services.selectpicker('refresh');
            $referral_id.val('');
            $doctors.selectpicker('refresh');
        });
    }

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
            $doctors.empty()
            $services.append('<option value="">Wybierz usługę</option>');
            var services = data['services'],
                referral_services = data['referral_services']
            if(referral_services) {
                $services.append('<optgroup label="Skierowania">');
                Object.keys(referral_services).forEach(function(k) {
                   $services.append(
                   `<option referral_id='${referral_services[k].ReferralId}' style='background: lightseagreen;'
                    value="${k}"> ${referral_services[k].Name} </option>`
                   );
                })
                $services.append('</optgroup>');

                $services.append('<optgroup label="Uslugi">');
                Object.keys(services).forEach(function(k) {
                   $services.append(`<option value="${k}"> ${services[k]} </option>`);
                })
                $services.append('</optgroup>');

            } else {
                Object.keys(services).forEach(function(k) {
                   $services.append(`<option value="${k}"> ${services[k]} </option>`);
                })
            }


            $doctors.selectpicker('refresh');
            $services.selectpicker('refresh');
            $referral_id.val('');
        });
    };

   var services_change_fn = function(e, params) {

        var city_id = $cities.find(":selected")[0].value;
        var service_id = $services.find(":selected")[0].value;
        var referral_id = $services.find(":selected").attr('referral_id')
        $referral_id.val(referral_id)
        var clinic_ids = $.map($(':selected', $clinics), function(option) {
         return option.value;
        });

        if(clinic_ids.length == 1 && clinic_ids[0] == -1) {
            clinic_ids = [];
        }

        var body = { city_id: city_id, service_id: service_id, referral_id: referral_id, clinic_ids: clinic_ids }

        $.post( "/doctors", body).done(function(data) {
            $doctors.empty()
            $doctors.append('<option value="-1"> Dowolny </option>');
            Object.keys(data).forEach(function(k) {
               $doctors.append(`<option value="${k}"> ${data[k]} </option>`);
            })
            $doctors.selectpicker('refresh');
        });
    };

     var doctors_change_fn = function(e, params) {

        var newValues = $($(this).val()).not(selectedDoctors).get();

        if(newValues[0] == -1 && $selected.length > 1) {
            $doctors.selectpicker('deselectAll')
            $doctors.selectpicker('val', '-1');
            $doctors.selectpicker('refresh');
        } else if (newValues[0] != -1 && selectedDoctors.includes("-1")) {
            $doctors.selectpicker('deselectAll')
            $doctors.selectpicker('val', newValues[0]);
            $doctors.selectpicker('refresh');
        }
        selectedDoctors = $(this).val();
    };

    $cities.on('change', cities_change_fn);
    $clinics.on('change', clinics_change_fn);
    $services.on('change', services_change_fn);
    $doctors.on('change', doctors_change_fn)
}

$(function() {

   input_controllers();
   time_controllers();
   date_controllers();

});


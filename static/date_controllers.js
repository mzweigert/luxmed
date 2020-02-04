var date_controllers = function() {
      var $date_from = $('#date-from');
      var $date_to = $('#date-to');
      var currentDate = new Date()
      $date_from.datetimepicker({
         format: 'L',
         locale: 'pl',
         defaultDate: currentDate
      });

        $date_to.datetimepicker({
            useCurrent: false, //Important! See issue #1075
               format: 'L',
                locale: 'pl',
                defaultDate: currentDate.setMonth(currentDate.getMonth() + 1)
        });
        $date_from.on("dp.change", function (e) {
            $date_to.data("DateTimePicker").minDate(e.date);
        });
        $date_to.on("dp.change", function (e) {
            $date_from.data("DateTimePicker").maxDate(e.date);
        });
}
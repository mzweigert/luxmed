var time_controllers = function() {

        var FROM_TIME = "6:00",
            TO_TIME = "22:00";

        $time_from = $('#time-from');
        $time_to = $('#time-to')

         $time_from.timepicker({
                    minuteStep: 1,
                    appendWidgetTo: 'body',
                    showMeridian: false,
                    defaultTime: FROM_TIME
         });

     $time_to.timepicker({
                minuteStep: 1,
                appendWidgetTo: 'body',
                showMeridian: false,
                defaultTime: TO_TIME
     });

      $time_from.timepicker().on('changeTime.timepicker', function(e) {
        if(e.time.hours < get_hours(FROM_TIME)) {
            $time_from.timepicker('setTime', TO_TIME);
        } else if (minutes_between($time_from.val(), $time_to.val()) < 60) {
           $time_from.timepicker('setTime', hours_offset($time_to.val(), -1));
        }
      });

      $time_to.timepicker().on('changeTime.timepicker', function(e) {
        hour = get_hours(TO_TIME)
        if(e.time.hours > hour || (e.time.hours >= hour && e.time.minutes > 0)) {
            $time_to.timepicker('setTime', TO_TIME);
        } else if (minutes_between($time_from.val(), $time_to.val()) < 60) {
            $time_to.timepicker('setTime', hours_offset($time_from.val(), 1));
        }
      });

      var get_hours = function (time) {
        return time.substr(0, time.indexOf(':'))
      }
       var get_minutes = function (time) {
        return time.substr(time.indexOf(':') + 1)
      }

      var minutes_between = function(time_from, time_to) {
        var startTime = new Date();
        startTime.setHours(get_hours(time_from), get_minutes(time_from), 0);
        var endTime = new Date();
        endTime.setHours(get_hours(time_to), get_minutes(time_to), 0);
        var difference;
        if(endTime.getTime() > startTime.getTime()) {
            difference = endTime.getTime() - startTime.getTime();
        } else {
            difference = startTime.getTime() - endTime.getTime();
        }
        return Math.abs(Math.round(difference / 60000));
      }

      var hours_offset = function(time, offset) {
        var startTime = new Date();
        startTime.setHours(get_hours(time), get_minutes(time), 0)
        startTime.setHours(startTime.getHours() + offset)
        return startTime.getHours() + ':' + startTime.getMinutes()
      }


    };